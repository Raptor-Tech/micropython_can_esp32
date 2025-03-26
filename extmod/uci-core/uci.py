
import struct
from binascii import crc_hqx

class SPIpacket:
  def __init__(self):
    self._status = None
    self._status_flag = False
    self.retry = 3
    self.response_timeout = 1.0
    self.notify_timeout = 0.0

  def set_status(self, value):
    self._status = value
    self._status_flag = True

  def status(self, timeout=None):
    return self._status

  def data(self):
    return self._data

  def response_bytes_required(self):
    return 0

  def notify_bytes_required(self):
    return 0

  def accept_response(self, header, consume):
    return False

  def accept_notification(self, header, consume):
    return False

  @staticmethod
  def compute_checksum(data):
    return crc_hqx(data, 0xFFFF)


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


class SPIqueue:
  def __init__(self):
    self.sendq = []
    self.respq = []

  def queue_packet(self, packet):
    self.sendq.append(packet)

  def irq_handler(self):
    pass  # Stub


class UCIqueue(SPIqueue):
  def __init__(self):
    super().__init__()

  def irq_handler(self):
    super().irq_handler()


class UCI:
  def __init__(self, spi, ce, cs, irq, sync, firmware=None):
    self.queue = UCIqueue()

  def send_command(self, gid, oid, payload=b''):
    packet = UCIcommand(gid, oid, payload)
    self.queue.queue_packet(packet)
    return packet
