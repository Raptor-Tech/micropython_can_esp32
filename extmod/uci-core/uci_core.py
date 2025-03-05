import machine
import time
import _thread

class UciCoreDriverSPI:
    def __init__(self, spi_id=1, baudrate=1000000, sck=18, mosi=23, miso=19, cs=5, irq=22):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.irq = machine.Pin(irq, machine.Pin.IN)
        
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck),
                               mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self.lock = _thread.allocate_lock()
        self.notification_queue = []  # Store asynchronous notifications

        self.cs.value(1)  # Deselect the UWB chip initially
        _thread.start_new_thread(self._notification_listener, ())  # Start IRQ listener
    
    def _notification_listener(self):
        """Thread to listen for incoming notifications based on IRQ pin."""
        while True:
            if self.irq.value() == 1:  # IRQ triggered
                notification = self.read_response(10)  # Adjust length as needed
                if notification:
                    self.notification_queue.append(notification)
            time.sleep(0.01)  # Small delay to avoid excessive polling

    def wait_for_notification(self, expected_code, timeout=2):
        """Wait for a specific notification with timeout."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            for i, notif in enumerate(self.notification_queue):
                if notif and notif[0] == expected_code:  # Assuming first byte is the identifier
                    return self.notification_queue.pop(i)
            time.sleep(0.01)  # Avoid busy-waiting
        return None  # Timeout occurred

    def reset_device(self):
        """Reset the UCI Core device via software command."""
        reset_command = b'\x00\x00\x00\x00'  # DEVICE_RESET_CMD per UCI spec
        self.send_command(reset_command)
        return self.wait_for_notification(0x01)  # Wait for DEVICE_STATUS_NTF

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
    
    def init_device(self):
        """Initialize UCI Core device."""
        self.reset_device()
        init_command = b'\x00\x01\x00\x00'  # CORE_GET_DEVICE_INFO_CMD
        self.send_command(init_command)
        return self.wait_for_notification(0x02)  # Wait for DEVICE_INFO_NTF

    def start_ranging(self, session_id):
        """Start a UWB ranging session and wait for confirmation."""
        command = b'\x00\x05' + session_id.to_bytes(4, 'little')
        self.send_command(command)
        return self.wait_for_notification(0x10)  # Wait for SESSION_STATUS_NTF

    def stop_ranging(self, session_id):
        """Stop a UWB ranging session and wait for confirmation."""
        command = b'\x00\x06' + session_id.to_bytes(4, 'little')
        self.send_command(command)
        return self.wait_for_notification(0x10)  # Wait for SESSION_STATUS_NTF

    def get_status(self):
        """Retrieve device status."""
        status_command = b'\x00\x02\x00\x00'  # CORE_GET_CAPS_INFO_CMD
        self.send_command(status_command)
        return self.read_response()
    
    def set_config(self, config_id, value):
        """Set a configuration parameter on the UCI device."""
        command = b'\x00\x03' + bytes([config_id, len(value)]) + value
        self.send_command(command)
        return self.wait_for_notification(0x20)  # Wait for CONFIG_STATUS_NTF

    def get_config(self, config_id):
        """Retrieve a configuration parameter from the UCI device."""
        command = b'\x00\x04' + bytes([config_id])
        self.send_command(command)
        return self.read_response()

    def get_session_count(self):
        """Retrieve the number of active UWB sessions."""
        command = b'\x00\x09'  # CORE_GET_SESSION_COUNT_CMD
        self.send_command(command)
        return self.read_response(2)
    
    def get_max_sessions(self):
        """Retrieve the maximum number of supported UWB sessions."""
        command = b'\x00\x0A'  # CORE_GET_MAX_SESSIONS_CMD
        self.send_command(command)
        return self.read_response(2)

if __name__ == "__main__":
    uci_driver = UciCoreDriverSPI()
    print("Resetting and Initializing UCI Core...")
    response = uci_driver.init_device()
    print("Response:", response)
    
    print("Starting ranging session...")
    start_resp = uci_driver.start_ranging(0x12345678)
    print("Start Ranging Response:", start_resp)
    
    print("Stopping ranging session...")
    stop_resp = uci_driver.stop_ranging(0x12345678)
    print("Stop Ranging Response:", stop_resp)

