import machine
import time
import _thread

class UciCoreDriverSPI:
    def __init__(self, spi_id=1, baudrate=1000000, sck=18, mosi=23, miso=19, cs=5, ce=6, irq=22):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.ce = machine.Pin(ce, machine.Pin.OUT)  # Chip Enable pin
        self.irq = machine.Pin(irq, machine.Pin.IN, machine.Pin.IRQ_FALLING, handler=self._irq_handler)
        
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck),
                               mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self.lock = _thread.allocate_lock()
        
        self.cs.value(1)  # Deselect the UWB chip initially
        self.ce.value(0)  # Keep Chip Enable low initially
        
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
        print("IRQ triggered - handling event")
    
    def send_command(self, command: bytes):
        """Send a command to the UCI Core over SPI."""
        with self.lock:
            self.cs.value(0)  # Select the UWB chip
            self.spi.write(command)
            time.sleep(0.01)  # Allow processing time
            self.cs.value(1)  # Deselect the UWB chip
    
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
            self.send_command(chunk)
            offset += chunk_size
            print(f"Firmware write progress: {offset}/{total_size} bytes")
        
        print("Firmware write complete!")
        return True

