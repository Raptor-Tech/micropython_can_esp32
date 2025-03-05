from uci_core_driver import UciCoreDriverSPI
import time

class UciManager:
    """High-level UWB session and configuration management."""
    def __init__(self):
        self.uci = UciCoreDriverSPI()
    
    def initialize_device(self):
        """Perform full device initialization and capability check."""
        print("Initializing UWB device...")
        response = self.uci.reset_device()
        if response:
            print("Device reset successfully.")
        device_info = self.uci.get_device_info()
        if device_info:
            print("Device Info:", device_info)
        else:
            print("Device initialization failed.")
        return device_info
    
    def configure_uwb(self, config_id, value):
        """Set a UWB configuration and ensure it applies correctly."""
        print(f"Setting config {config_id} to {value}...")
        response = self.uci.set_config(config_id, value)
        if response:
            print("Configuration applied successfully.")
        else:
            print("Configuration failed.")
        return response
    
    def start_session(self, session_id):
        """Start a new UWB session and verify activation."""
        print(f"Starting UWB session {session_id}...")
        response = self.uci.start_ranging(session_id)
        if response:
            print("Session started successfully.")
        else:
            print("Failed to start session.")
        return response
    
    def stop_session(self, session_id):
        """Stop an active UWB session."""
        print(f"Stopping UWB session {session_id}...")
        response = self.uci.stop_ranging(session_id)
        if response:
            print("Session stopped successfully.")
        else:
            print("Failed to stop session.")
        return response
    
    def get_active_sessions(self):
        """Retrieve the number of active UWB sessions."""
        response = self.uci.get_session_count()
        session_count = int.from_bytes(response, 'little') if response else 0
        print(f"Active UWB Sessions: {session_count}")
        return session_count
    
    def get_max_sessions(self):
        """Retrieve the maximum number of supported UWB sessions."""
        response = self.uci.get_max_sessions()
        max_sessions = int.from_bytes(response, 'little') if response else 0
        print(f"Max Supported UWB Sessions: {max_sessions}")
        return max_sessions
    
    def get_uwbs_state(self):
        """Retrieve the current UWB state."""
        return self.uci.get_uwbs_state()
    
if __name__ == "__main__":
    manager = UciManager()
    manager.initialize_device()
    manager.configure_uwb(0x01, b'\x01')
    manager.start_session(0x12345678)
    time.sleep(5)  # Simulate active sessionmanager.get_active_sessions()
    manager.stop_session(0x12345678)
    manager.get_max_sessions()
    print("Current UWBS State:", manager.get_uwbs_state())

