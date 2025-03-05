import machine
import time
import _thread

class UciCoreDriverSPI:
    def __init__(self, spi_id=2, baudrate=1000000, sck=20, mosi=8, miso=19, cs=3, ce=18, irq=9):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.ce = machine.Pin(ce, machine.Pin.OUT)  # Chip Enable pin
        self.irq = machine.Pin(irq, machine.Pin.IN)
        self.irq.irq(trigger=machine.Pin.IRQ_FALLING, handler=self._irq_handler)
        
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck),
                               mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self.lock = _thread.allocate_lock()
        self.notification_semaphore = _thread.allocate_lock()
        self.notification_data = None
        
        self.cs.value(1)  # Deselect the UWB chip initially
        self.ce.value(0)  # Keep Chip Enable low initially
        
    def _irq_handler(self, pin):
        """IRQ handler triggered on notification arrival."""
        self.notification_data = self.read_response(10)
        if not self.notification_semaphore.locked():
            self.notification_semaphore.acquire()
    
    def wait_for_notification(self, expected_code, timeout=5):
        """Wait for a specific notification using a semaphore, with timeout."""
        if not self.notification_semaphore.acquire(timeout=timeout):
            print("Notification timeout occurred")
            return None
        if self.notification_data and self.notification_data[0] == expected_code:
            return self.notification_data
        return None
    
    def send_command(self, command: bytes):
        """Send a command to the UCI Core over SPI."""
        with self.lock:
            self.cs.value(0)  # Select the UWB chip
            self.spi.write(command)
            time.sleep(0.01)  # Allow processing time
            self.cs.value(1)  # Deselect the UWB chip
    
    def read_response(self, length=10):
        """Read response from UCI Core via SPI."""
        with self.lock:
            self.cs.value(0)  # Select the UWB chip
            response = self.spi.read(length)  # Read response bytes
            self.cs.value(1)  # Deselect the UWB chip
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
            self.send_command(chunk)
            offset += chunk_size
            print(f"Firmware write progress: {offset}/{total_size} bytes")
        
        print("Firmware write complete!")
        return True
