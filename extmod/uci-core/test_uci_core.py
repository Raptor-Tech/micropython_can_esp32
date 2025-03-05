import pytest
from unittest.mock import MagicMock
from uci_core_driver import UciCoreDriverSPI  # Assuming the driver is in uci_core_driver.py

class TestUciCoreDriverSPI:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.driver = UciCoreDriverSPI()
        self.driver.send_command = MagicMock()
        self.driver.read_response = MagicMock()
    
    def test_init_device(self):
        self.driver.read_response.return_value = b'\x01\x02'  # Mock response
        response = self.driver.init_device()
        self.driver.send_command.assert_called_once()
        assert response == b'\x01\x02'
    
    def test_get_status(self):
        self.driver.read_response.return_value = b'\x00\x01'
        response = self.driver.get_status()
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x01'
    
    def test_set_config(self):
        self.driver.read_response.return_value = b'\x00\x01'
        response = self.driver.set_config(0x01, b'\x01')
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x01'
    
    def test_get_config(self):
        self.driver.read_response.return_value = b'\x00\x02'
        response = self.driver.get_config(0x01)
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x02'
    
    def test_start_ranging(self):
        self.driver.read_response.return_value = b'\x00\x01'
        response = self.driver.start_ranging(0x12345678)
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x01'
    
    def test_stop_ranging(self):
        self.driver.read_response.return_value = b'\x00\x01'
        response = self.driver.stop_ranging(0x12345678)
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x01'
    
    def test_get_azimuth_elevation(self):
        self.driver.read_response.return_value = b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B'
        response = self.driver.get_azimuth_elevation(0x12345678)
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B'
    
    def test_scan_uwb_devices(self):
        self.driver.read_response.return_value = b'\x00' * 64
        response = self.driver.scan_uwb_devices()
        self.driver.send_command.assert_called_once()
        assert response == b'\x00' * 64
    
    def test_get_session_count(self):
        self.driver.read_response.return_value = b'\x00\x02'
        response = self.driver.get_session_count()
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x02'
    
    def test_get_max_sessions(self):
        self.driver.read_response.return_value = b'\x00\x05'
        response = self.driver.get_max_sessions()
        self.driver.send_command.assert_called_once()
        assert response == b'\x00\x05'

