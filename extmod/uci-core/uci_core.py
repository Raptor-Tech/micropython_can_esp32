import machine
import time
import _thread

# UCI Command and Notification Constants
DEVICE_RESET_CMD = b'\x00\x00\x00\x00'
CORE_GET_DEVICE_INFO_CMD = b'\x00\x01\x00\x00'
CORE_GET_CAPS_INFO_CMD = b'\x00\x02\x00\x00'
CORE_SET_CONFIG_CMD = b'\x00\x03'
CORE_GET_CONFIG_CMD = b'\x00\x04'
CORE_START_RANGING_CMD = b'\x00\x05'
CORE_STOP_RANGING_CMD = b'\x00\x06'
CORE_GET_SESSION_COUNT_CMD = b'\x00\x09'
CORE_GET_MAX_SESSIONS_CMD = b'\x00\x0A'

# UCI Notification Codes
DEVICE_STATUS_NTF = 0x01
DEVICE_INFO_NTF = 0x02
SESSION_STATUS_NTF = 0x10
CONFIG_STATUS_NTF = 0x20

# UWBS States (from UCI Spec Section 4)
UWBS_STATE_INACTIVE = 0
UWBS_STATE_IDLE = 1
UWBS_STATE_ACTIVE = 2

class UciCoreDriverSPI:
    def __init__(self, spi_id=1, baudrate=1000000, sck=18, mosi=23, miso=19, cs=5, irq=22):
        """Initialize the UCI Core driver with SPI and control pins."""
        self.cs = machine.Pin(cs, machine.Pin.OUT)
        self.irq = machine.Pin(irq, machine.Pin.IN, machine.Pin.IRQ_FALLING, handler=self._irq_handler)
        
        self.spi = machine.SPI(spi_id, baudrate=baudrate, sck=machine.Pin(sck),
                               mosi=machine.Pin(mosi), miso=machine.Pin(miso))
        self.lock = _thread.allocate_lock()
        self.notification_semaphore = _thread.allocate_lock()  # Acts as a semaphore
        self.notification_data = None  # Stores the latest notification data
        self.notification_callback = None  # User-defined callback function
        self.uwbs_state = UWBS_STATE_INACTIVE  # Initial UWBS state

        self.cs.value(1)  # Deselect the UWB chip initially

    def _irq_handler(self, pin):
        """IRQ handler triggered on notification arrival."""
        try:
            notification = self.read_response(10)  # Adjust length as needed
            if notification:
                self.notification_data = notification
                self._update_uwbs_state(notification)  # Update UWBS state
                if self.notification_callback:
                    self.notification_callback(notification)
                if not self.notification_semaphore.locked():
                    self.notification_semaphore.acquire()  # Release waiting threads
        except Exception as e:
            print("Error in IRQ handler:", e)
    
    def _update_uwbs_state(self, notification):
        """Update the UWBS state based on notifications."""
        notif_code = notification[0]  # Assuming first byte is the identifier
        if notif_code == DEVICE_STATUS_NTF:
            self.uwbs_state = UWBS_STATE_IDLE  # After reset, device goes to IDLE
        elif notif_code == SESSION_STATUS_NTF:
            if notification[1] == 0x01:  # Assuming 0x01 means session started
                self.uwbs_state = UWBS_STATE_ACTIVE
            elif notification[1] == 0x00:  # Assuming 0x00 means session stopped
                self.uwbs_state = UWBS_STATE_IDLE
    
    def set_notification_callback(self, callback):
        """Set a user-defined callback function for notifications."""
        self.notification_callback = callback

    def wait_for_notification(self, expected_code, timeout=2):
        """Wait for a specific notification using a semaphore, with timeout."""
        try:
            if not self.notification_semaphore.acquire(timeout=timeout):
                raise TimeoutError("Timeout waiting for notification")
            if self.notification_data and self.notification_data[0] == expected_code:
                return self.notification_data
        except TimeoutError:
            print("Notification timeout occurred")
        return None  # Timeout or unexpected notification

    def reset_device(self):
        """Reset the UCI Core device via software command."""
        self.send_command(DEVICE_RESET_CMD)
        return self.wait_for_notification(DEVICE_STATUS_NTF)

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
    
    def get_device_info(self):
        """Retrieve device information."""
        self.send_command(CORE_GET_DEVICE_INFO_CMD)
        return self.wait_for_notification(DEVICE_INFO_NTF)
    
    def get_uwbs_state(self):
        """Retrieve the current UWB state."""
        return self.uwbs_state

