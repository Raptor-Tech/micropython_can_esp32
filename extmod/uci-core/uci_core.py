import machine
import time
import _thread
import binascii

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
        
        # Perform low-level initialization including firmware loading
        self.low_level_initialize('H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
        #self.low_level_initialize('H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
    
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
        """Wait for a specific notification using a semaphore and a timer-based timeout."""
        def timeout_handler(timer):
            self.notification_semaphore.release()  # Unblock waiting thread on timeout
        
        timer = machine.Timer(-1)
        timer.init(period=timeout * 1000, mode=machine.Timer.ONE_SHOT, callback=timeout_handler)
        
        try:
            self.notification_semaphore.acquire()  # Block until released by IRQ or timeout
            if self.notification_data and self.notification_data[0] == expected_code:
                timer.deinit()
                return self.notification_data
        except:
            print("Notification timeout occurred")
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
            self.send_command(chunk)
            offset += chunk_size
            print(f"Firmware write progress: {offset}/{total_size} bytes\r", end="")
        
        print("Firmware write complete!")
        return True

