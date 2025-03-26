from  machine import SPI, Pin
import struct
import time
import _thread
import threading
from binascii import crc_hqx

_buffsize = 4096


class HBCIqueue(SPIqueue):
  def __init__(self, spiQ: SPIqueue):
    super().__init__(spiQ.spi, spiQ.irqPin, spiQ.syncPin, spiQ.csPin, spiQ.cePin)
    self.cePin.value(0)
    time.sleep(10)
    self.cePin.value(1)

  def _firmware_upload(self):
    f = open(self.firmware, "rb")
    while (chunk := f.read(CHUNKSIZE)):
      packet = HBCIfirmware(chunk)
      self.queue_packet(packet)
      if CHUNKSIZE > len(chunk):
        break

  def rd_handshake():
    while 1:
      if self.intPin.value() == 0:
        break

  def wr_handshake():
    while 1:
      if self.irdPin.value() == 0:
        break

  def irq_handler(self, pin):
    print("HBCI IRQ: Data ready for processing.")



class HBCIpacket(SPIpacket):
  HEADER = 0xAA55
  HEADER_FORMAT = '>HBB'
  CHECKSUM_FORMAT = '>H'

  def __init__(self):
    pass

  def accept_response(self, header, consume):
    pass


class HBCIcommand(HBCIpacket):
  def __init__(self, cla: int, ins: int, payload: bytes = b''):
    self.cla = cla
    self.ins = ins
    self.payload = payload
    self.length = len(payload)
    header = struct.pack(self.HEADER_FORMAT, self.HEADER, cla, ins)
    length_byte = bytes([len(self.payload)])
    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + length_byte + payload))
    self._data = header + length_byte + payload + crc

  def data(self) -> bytes:
    return self._data

  def response_bytes_required(self) -> int:
    return len(self._data)


class HBCIresponse(HBCIpacket):
  def __init__(self, payload: bytes):
    self.payload = payload
    self.valid = False
    if len(raw_data) >= 6:
      header = raw_data[:2]
      self.cla = raw_data[2]
      self.ins = raw_data[3]
      self.length = raw_data[4]
      self.payload = raw_data[5:-2]
      self.crc_received = struct.unpack(self.CHECKSUM_FORMAT, raw_data[-2:])[0]
      calc_crc = self.compute_checksum(raw_data[:-2])
      self.valid = self.crc_received == calc_crc


class HBCIfirmware(HBCIpacket):
  def __init__(self, chunk: bytes):
    self.cla = 0x13
    self.ins = 0x04
    self.payload = chunk
    self.length = len(self.payload)
    header = struct.pack(self.HEADER_FORMAT, self.HEADER, self.cla, self.ins)
    length_byte = bytes([self.length])
    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + length_byte + self.payload))
    self._data = header + length_byte + self.payload + crc
    self.retry = 3
    self._status = None
    self._status_sema = threading.Semaphore(0)

  def data(self) -> bytes:
    return self._data

  def response_bytes_required(self) -> int:
    return 8

  def accept_response(self, header_chk, consume) -> bool:
    response = consume(8)
    if len(response) != 8:
      self.set_status("FAIL")
      return True

    hdr, cla, ins, length = struct.unpack('>HBBB', response[:5])

    if ins == 0x81:
      self.set_status("ACK")
    elif ins in (0x82, 0x83):
      self.retry -= 1
      self.set_status("RETRY" if self.retry > 0 else "FAIL")
    else:
      self.set_status("FAIL")

    return True

