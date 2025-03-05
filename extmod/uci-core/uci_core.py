import machine
import time
import _thread

class UciCoreDriverSPI:
    def __init__(self, spi_id=1, baudrate=1000000, sck=18, mosi=23, miso=19, cs=5, rst=4, irq=22):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.rst = machine.Pin(rst, machine.Pin.OUT)
        self.irq = machine.Pin(irq, machine.Pin.IN)
        
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck),
                               mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self.lock = _thread.allocate_lock()
        
        self.cs.value(1)  # Deselect the UWB chip initially
        self.rst.value(1)  # Set reset to default high

    def reset_device(self):
        """Reset the UCI Core device."""
        self.rst.value(0)
        time.sleep(0.1)
        self.rst.value(1)
        time.sleep(0.1)

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
        return self.read_response()

    def get_status(self):
        """Retrieve device status."""
        status_command = b'\x00\x02\x00\x00'  # CORE_GET_CAPS_INFO_CMD
        self.send_command(status_command)
        return self.read_response()
    
    def set_config(self, config_id, value):
        """Set a configuration parameter on the UCI device."""
        command = b'\x00\x03' + bytes([config_id, len(value)]) + value
        self.send_command(command)
        return self.read_response()

    def get_config(self, config_id):
        """Retrieve a configuration parameter from the UCI device."""
        command = b'\x00\x04' + bytes([config_id])
        self.send_command(command)
        return self.read_response()

    def start_ranging(self, session_id):
        """Start a UWB ranging session."""
        command = b'\x00\x05' + session_id.to_bytes(4, 'little')
        self.send_command(command)
        return self.read_response()

    def stop_ranging(self, session_id):
        """Stop a UWB ranging session."""
        command = b'\x00\x06' + session_id.to_bytes(4, 'little')
        self.send_command(command)
        return self.read_response()
    
    def get_azimuth_elevation(self, session_id):
        """Retrieve azimuth and elevation angles for direction finding."""
        command = b'\x00\x07' + session_id.to_bytes(4, 'little')
        self.send_command(command)
        return self.read_response(12)  # Expecting azimuth and elevation data
    
    def scan_uwb_devices(self):
        """Scan and identify nearby UWB tags and anchors."""
        scan_command = b'\x00\x08'  # Placeholder command for scanning
        self.send_command(scan_command)
        return self.read_response(64)  # Expecting a list of detected devices
    
    def get_session_count(self):
        """Retrieve the number of active UWB sessions."""
        command = b'\x00\x09'  # CORE_GET_SESSION_COUNT_CMD
        self.send_command(command)
        return self.read_response(2)  # Expecting a 2-byte response for session count
    
    def get_max_sessions(self):
        """Retrieve the maximum number of supported UWB sessions."""
        command = b'\x00\x0A'  # CORE_GET_MAX_SESSIONS_CMD (hypothetical)
        self.send_command(command)
        return self.read_response(2)  # Expecting a 2-byte response for max session count

if __name__ == "__main__":
    uci_driver = UciCoreDriverSPI()
    print("Resetting and Initializing UCI Core...")
    response = uci_driver.init_device()
    print("Response:", response)
    
    print("Getting status...")
    status = uci_driver.get_status()
    print("Status:", status)
    
    print("Setting a config...")
    set_resp = uci_driver.set_config(0x01, b'\x01')
    print("Set Config Response:", set_resp)
    
    print("Getting config...")
    get_resp = self.driver.get_config(0x01)
    print("Get Config Response:", get_resp)
    
    print("Starting ranging session...")
    start_resp = uci_driver.start_ranging(0x12345678)
    print("Start Ranging Response:", start_resp)
    
    print("Getting Azimuth and Elevation...")
    df_resp = uci_driver.get_azimuth_elevation(0x12345678)
    print("Azimuth & Elevation Response:", df_resp)
    
    print("Scanning for UWB devices...")
    scan_resp = uci_driver.scan_uwb_devices()
    print("Detected UWB Devices:", scan_resp)
    
    print("Getting session count...")
    session_count_resp = uci_driver.get_session_count()
    print("Active UWB Sessions:", session_count_resp)
    
    print("Getting max supported sessions...")
    max_sessions_resp = uci_driver.get_max_sessions()
    print("Max UWB Sessions Supported:", max_sessions_resp)
    
    print("Stopping ranging session...")
    stop_resp = uci_driver.stop_ranging(0x12345678)
    print("Stop Ranging Response:", stop_resp)

