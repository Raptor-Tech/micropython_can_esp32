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
        
        # Explicitly configure GPIO before SPI initialization
        sck_pin = machine.Pin(sck, machine.Pin.OUT, pull=machine.Pin.PULL_DOWN)
        mosi_pin = machine.Pin(mosi, machine.Pin.OUT)
        miso_pin = machine.Pin(miso, machine.Pin.IN, pull=machine.Pin.PULL_UP)  # Enable pull-up for MISO
        
        # Route GPIOs through GPIO Matrix
        esp32.gpio_matrix_out(sck, esp32.SPICLK_OUT, False, False)
        esp32.gpio_matrix_out(mosi, esp32.SPID_OUT, False, False)
        esp32.gpio_matrix_in(miso, esp32.SPID_IN, False)
        
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
    
    def _irq_handler(self, pin):
        """IRQ handler triggered on notification arrival."""
        self.notification_data = self.read_response(10)
        if not self.notification_semaphore.locked():
            self.notification_semaphore.release()
    
    def wait_for_notification(self, expected_code, timeout=5):
        """Wait for a specific notification using a semaphore with timeout support."""
        if not self.notification_semaphore.acquire(timeout=timeout):
            print("Notification timeout occurred")
            return None
        if self.notification_data and self.notification_data[0] == expected_code:
            return self.notification_data
        return None
    
    def send_command(self, command: bytes):
        """Send a command to the UCI Core over SPI with diagnostic output."""
        with self.lock:
            self.cs.value(0)  # Select the UWB chip
            print(f"Sending SPI command: {binascii.hexlify(command).decode()}")
            self.spi.write(command)
            time.sleep(0.01)  # Allow processing time
            self.cs.value(1)  # Deselect the UWB chip
    
    def read_response(self, length=10):
        """Read response from UCI Core via SPI with diagnostic output."""
        with self.lock:
            self.cs.value(0)  # Select the UWB chip
            response = self.spi.read(length)  # Read response bytes
            self.cs.value(1)  # Deselect the UWB chip
        print(f"Received SPI response: {binascii.hexlify(response).decode()}")
        return response
    
    def write_firmware_to_device(self, firmware_path: str):
        """Write firmware from an external .bin file to the UWB chip over SPI."""
        print(f"Loading firmware from {firmware_path}...")
        
        try:
            with open(firmware_path, "rb") as f:
                firmware_data = f.read()
        except Exception as e:
            print(f"Error reading firmware file: {e}")
            return False
        
        print("Writing firmware to the UWB chip...")
        chunk_size = 256  # SPI transfer chunk size
        total_size = len(firmware_data)
        offset = 0
        
        while offset < total_size:
            chunk = firmware_data[offset:offset + chunk_size]
            
            with self.lock:
                self.cs.value(0)  # Select the UWB chip before writing
                self.spi.write(chunk)  # Write chunk over SPI
                self.cs.value(1)  # Deselect the chip after writing
            
            offset += chunk_size
            print(f"Firmware write progress: {offset}/{total_size} bytes\r", end="")
        
        print("Firmware write complete!")
        return True

