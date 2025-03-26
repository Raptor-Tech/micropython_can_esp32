import threading
import time

class UciTransport:
    """Handles UCI transport layer, queues commands, awaits responses, and manages notifications."""
    def __init__(self, spi_interface):
        self.spi = spi_interface
        self.command_queue = []
        self.response_queue = []
        self.notification_queue = []
        self.lock = threading.Lock()
        self.response_event = threading.Event()
    
    def queue_command(self, command):
        """Queue a command for sending and return once a response is received."""
        with self.lock:
            self.command_queue.append(command)
        return self._process_command()
    
    def _process_command(self):
        """Process the next command in the queue, handle fragmentation, and await response."""
        with self.lock:
            if self.command_queue:
                command = self.command_queue.pop(0)
                packets = self._split_command(command)
                for packet in packets:
                    response = self.spi.send_command(packet)
                    self.response_queue.append(response)
        return self.wait_for_response()
    
    def _split_command(self, command, max_packet_size=10):
        """Split a large command into smaller packets."""
        return [command[i:i+max_packet_size] for i in range(0, len(command), max_packet_size)]
    
    def wait_for_response(self, timeout=5):
        """Wait until a response is available or timeout occurs."""
        self.response_event.clear()
        if not self.response_event.wait(timeout):
            return None  # Timeout
        
        with self.lock:
            if self.response_queue:
                return self.response_queue.pop(0)
        return None
    
    def handle_notification(self, notification):
        """Queue received notifications for later processing."""
        with self.lock:
            self.notification_queue.append(notification)
    
    def get_next_notification(self):
        """Retrieve the next queued notification."""
        with self.lock:
            if self.notification_queue:
                return self.notification_queue.pop(0)
        return None

