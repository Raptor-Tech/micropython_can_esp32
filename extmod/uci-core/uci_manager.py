from uci_core import UciCoreDriverSPI
import time

# UCI Command Constants
DEVICE_RESET_CMD = b'\x00\x00\x00\x00'
CORE_APPLY_CALIBRATION_CMD = b'\x00\x0C'
CORE_GET_CAPS_INFO_CMD = b'\x00\x02\x00\x00'
CORE_SET_CONFIG_CMD = b'\x00\x03'
CORE_GET_CONFIG_CMD = b'\x00\x04'
CORE_START_RANGING_CMD = b'\x00\x05'
CORE_STOP_RANGING_CMD = b'\x00\x06'
CORE_GET_SESSION_COUNT_CMD = b'\x00\x09'
CORE_GET_MAX_SESSIONS_CMD = b'\x00\x0A'

# UCI Notification Codes
DEVICE_STATUS_NTF = 0x01
CALIBRATION_APPLY_NTF = 0x40
CONFIG_STATUS_NTF = 0x20
SESSION_STATUS_NTF = 0x10

# UWB States
UWBS_STATE_INACTIVE = 0
UWBS_STATE_IDLE = 1
UWBS_STATE_ACTIVE = 2

class UciManager:
    """High-level UWB session and configuration management."""
    def __init__(self):
        self.uci = UciCoreDriverSPI()
        self.uwbs_state = UWBS_STATE_INACTIVE  # Initial UWB state
        self.notification_data = None
    
    def wait_for_notification(self, expected_code, timeout=5):
        """Wait for a specific notification using a semaphore, with timeout."""
        if not self.uci.notification_semaphore.acquire(timeout=timeout):
            print("Notification timeout occurred")
            return None
        if self.uci.notification_data and self.uci.notification_data[0] == expected_code:
            return self.uci.notification_data
        return None
    
    def initialize_device(self):
        """Perform full device initialization and capability check."""
        print("Initializing UWB device...")
        
        # Reset device after firmware is loaded
        self.uci.send_command(DEVICE_RESET_CMD)
        response = self.wait_for_notification(DEVICE_STATUS_NTF)
        if not response:
            print("Device reset failed.")
            return False
        print("Device reset successfully.")
        
        # Apply calibration values
        if not self.apply_calibration():
            print("Calibration application failed.")
            return False
        
        print("Device initialized and calibrated successfully.")
        self.uwbs_state = UWBS_STATE_IDLE
        return True
    
    def apply_calibration(self):
        """Apply calibration values after device reset."""
        print("Applying calibration values...")
        self.uci.send_command(CORE_APPLY_CALIBRATION_CMD)
        response = self.wait_for_notification(CALIBRATION_APPLY_NTF, timeout=5)
        if response:
            print("Calibration applied successfully.")
            return True
        print("Calibration application failed.")
        return False
    
    def configure_uwb(self, config_id, value):
        """Set a UWB configuration and ensure it applies correctly."""
        print(f"Setting config {config_id} to {value}...")
        command = CORE_SET_CONFIG_CMD + bytes([config_id, len(value)]) + value
        self.uci.send_command(command)
        response = self.wait_for_notification(CONFIG_STATUS_NTF)
        return response is not None
    
    def get_config(self, config_id):
        """Retrieve a configuration parameter from the UCI device."""
        command = CORE_GET_CONFIG_CMD + bytes([config_id])
        self.uci.send_command(command)
        return self.uci.read_response()
    
    def start_session(self, session_id):
        """Start a new UWB session and verify activation."""
        print(f"Starting UWB session {session_id}...")
        command = CORE_START_RANGING_CMD + session_id.to_bytes(4, 'little')
        self.uci.send_command(command)
        response = self.wait_for_notification(SESSION_STATUS_NTF)
        if response:
            self.uwbs_state = UWBS_STATE_ACTIVE
            return True
        return False
    
    def stop_session(self, session_id):
        """Stop an active UWB session."""
        print(f"Stopping UWB session {session_id}...")
        command = CORE_STOP_RANGING_CMD + session_id.to_bytes(4, 'little')
        self.uci.send_command(command)
        response = self.wait_for_notification(SESSION_STATUS_NTF)
        if response:
            self.uwbs_state = UWBS_STATE_IDLE
            return True
        return False
    
    def get_active_sessions(self):
        """Retrieve the number of active UWB sessions."""
        self.uci.send_command(CORE_GET_SESSION_COUNT_CMD)
        response = self.uci.read_response(2)
        return int.from_bytes(response, 'little') if response else 0
    
    def get_max_sessions(self):
        """Retrieve the maximum number of supported UWB sessions."""
        self.uci.send_command(CORE_GET_MAX_SESSIONS_CMD)
        response = self.uci.read_response(2)
        return int.from_bytes(response, 'little') if response else 0
    
    def get_uwbs_state(self):
        """Retrieve the current UWB state."""
        return self.uwbs_state
    
if __name__ == "__main__":
    manager = UciManager()
    manager.initialize_device()
    manager.configure_uwb(0x01, b'\x01')
    manager.start_session(0x12345678)
    time.sleep(5)  # Simulate active session
    print("Active Sessions:", manager.get_active_sessions())
    manager.stop_session(0x12345678)
    print("Max Sessions Supported:", manager.get_max_sessions())
    print("Current UWBS State:", manager.get_uwbs_state())
