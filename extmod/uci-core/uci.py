# UCI Protocol State Implementation
# Used after firmware upload to communicate with the UWB stack in UCI mode.
# May be initialized directly or transitioned to by HBCIqueue after upload.

from  machine import SPI, Pin
import struct
import time
import _thread
from semaphore import CountingSemaphore
from spi import SPIqueue, SPIpacket

class UCIqueue(SPIqueue):
  def __init__(self, spiQ: SPIqueue):
    self.spi = spiQ.spi
    self.cs = spiQ.cs
    self.ce = spiQ.ce
    self.irq = spiQ.irq
    self.sync = spiQ.sync
    self.firmware = spiQ.firmware

    return self

  def irq_handler(self):
    super().irq_handler()


class UCIpacket(SPIpacket):
  HEADER = 0xAA55
  HEADER_FORMAT = '>HBB'
  CHECKSUM_FORMAT = '>H'

  def __init__(self, gid, oid, payload=b''):
    super().__init__()
    self.gid = gid
    self.oid = oid
    self.payload = payload
    self.length = len(payload)
    header = struct.pack(self.HEADER_FORMAT, self.HEADER, gid, oid)
    length_byte = bytes([self.length])
    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + length_byte + payload))
    self._data = header + length_byte + payload + crc

  def response_bytes_required(self):
    return 8  # header + gid + oid + len + 0-payload + crc

  def accept_response(self, header_chk, consume):
    if len(header_chk) < 5:
      return False
    hdr, gid, oid, length = struct.unpack('>HBBBx', header_chk[:5] + b'\x00')
    if hdr != self.HEADER or gid != self.gid or oid != self.oid:
      return False
    _ = consume(8)
    self.set_status("ACK")
    return True


class UCIcommand(UCIpacket):
  def __init__(self, gid, oid, payload=b''):
    super().__init__(gid, oid, payload)


class UCIresponse(UCIpacket):
  def __init__(self, raw_bytes):
    super().__init__(0, 0)
    self.raw = raw_bytes
    self.parse_header()

  def parse_header(self):
    self.header = struct.unpack('>HBB', self.raw[:4])
    self.payload = self.raw[4:-2]



class UCI:
  def __init__(self, spi, ce, cs, irq, sync, firmware=None):
    self.queue = UCIqueue()

  def send_command(self, gid, oid, payload=b''):
    packet = UCIcommand(gid, oid, payload)
    self.queue.queue_packet(packet)
    return packet
