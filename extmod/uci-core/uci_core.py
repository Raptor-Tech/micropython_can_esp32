import machine
import time
import _thread
import binascii
import esp32

class UciCoreDriverSPI:
    def __init__(self, firmware_path: str, spi_id=2, baudrate=1000000, sck=20, mosi=8, miso=19, cs=3, ce=18, irq=9):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.ce = machine.Pin(ce, machine.Pin.OUT)  # Chip Enable pin
        self.irq = machine.Pin(irq, machine.Pin.IN)
        self.irq.irq(trigger=machine.Pin.IRQ_FALLING, handler=self._irq_handler)
        
        # Attempt to disable USB-OTG to free GPIO19 & GPIO20 at runtime
        try:
            esp32.rom.esp_usb_otg_disable()
            print("USB-OTG disabled successfully.")
        except AttributeError:
            print("USB-OTG disable function not available in this firmware.")
        
        # Explicitly configure GPIO before SPI initialization
        sck_pin = machine.Pin(sck, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN)
        mosi_pin = machine.Pin(mosi, machine.Pin.OUT)
        miso_pin = machine.Pin(miso, machine.Pin.IN, pull=machine.Pin.PULL_UP)  # Enable pull-up for MISO
        
        # Ensure GPIO19 and GPIO20 are properly initialized for SPI function
        sck_pin.init(mode=machine.Pin.OUT, pull=machine.Pin.PULL_DOWN)
        miso_pin.init(mode=machine.Pin.IN, pull=machine.Pin.PULL_UP)
        
        # Configure SPI with manually initialized GPIO
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=sck_pin, mosi=mosi_pin, miso=miso_pin)
        
        self.lock = _thread.allocate_lock()
        self.notification_semaphore = _thread.allocate_lock()
        self.notification_data = None
        
        self.cs.value(1)  # Deselect the UWB chip initially
        self.ce.value(0)  # Keep Chip Enable low initially
        
        # Perform low-level initialization including firmware loading
        self.low_level_initialize(firmware_path)
    
    def low_level_initialize(self, firmware_path: str):
        """Perform low-level initialization including firmware download from external file."""
        print("Starting low-level initialization...")
        
        # Enable chip
        self.ce.value(1)
        time.sleep(0.01)  # Allow stabilization
        
        # Load and write firmware from file
        if not self.write_firmware_to_device(firmware_path):
            print("Firmware write failed.")
            return False
        
        print("Low-level initialization complete.")
        return True

