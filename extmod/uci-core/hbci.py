# HBCI Protocol State Implementation
# This module implements the HBCIqueue class for managing SR150 firmware upload.
# It acts as a temporary protocol state until UCI mode is entered.
# State transitions are managed within _firmware_upload().

from  machine import SPI, Pin
import struct
import time
import _thread



class HBCIqueue(SPIqueue):

  CHUNKSIZE = 240

  def __init__(self, spiQ: SPIqueue):
    self.__dict__ = spiQ.__dict__

    _firmware_upload(self.firmware())

  @staticmethod
  def crc_16(data: bytes, poly: int = 0x1021, init: int = 0xFFFF) -> int:
    crc = init
    for byte in data:
      crc ^= byte << 8
      for _ in range(8):
        if crc & 0x8000:
          crc = (crc << 1) ^ poly
        else:
          crc <<= 1
        crc &= 0xFFFF
    return crc

  def _firmware_upload(self):
    """Performs firmware upload using HBCI protocol.
    Transitions to UCIqueue state on completion.
    """
    # --- Firmware upload sequence ---
    
    # Reset Chip
    self.cePin.value(0)
    time.sleep(0.010)
    self.cePin.value(1)

    
    self.queue_packet(HBCIStartFirmwareTransfer())  # Start transfer (optional flags can be added)

    f = open(self.firmware, "rb")
    while (clen:= len(chunk := f.read(CHUNKSIZE))):
      packet = HBCIfirmwareChunk(chunk)
      self.queue_packet(packet)
      if CHUNKSIZE > clen:  # Last Chunk -- Already tested > 0 by while clause
        break
    
    self.queue_packet(HBCIFinalizeFirmware())  # Finalize and boot into UCI

    # --- State transition logic (optional) ---
    from uci import UCIqueue
    new_state = UCIqueue(self.spi, self.ce, self.cs, self.irq, self.sync)
    self.__class__ = new_state.__class__
    self.__dict__ = new_state.__dict__

  def rd_handshake(self):
    while 1:
      if self.irqPin.value() == 0:
        break

  def wr_handshake(self):
    while 1:
      if self.irqPin.value() == 0:
        break

  def irq_handler(self, pin):
    print("HBCI IRQ: Data ready for processing.")



class HBCIpacket(SPIpacket):
  HEADER_SIZE = 5
  PACKET_ID = 0xAA55
  HEADER_FORMAT = '>HBBB'
  CHECKSUM_FORMAT = '>H'

  def __init__(self):
    super().__init__()

  def accept_response(self, header, consume):
    pass

class HBCIcommand(HBCIpacket):
  def __init__(self, cla: int, ins: int, payload: bytes = b''):
    super().__init__()
#    self.cla = cla
#    self.ins = ins
    self.payload = payload
    self.length = len(payload)
    length_byte = bytes([len(self.payload)])
    header = struct.pack(self.HEADER_FORMAT, self.PACKET_ID, cla, ins, len(payload))
    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + length_byte + payload))
    self._data = header + length_byte + payload + crc

  def cla(self):
    return self.header[-3]

  def ins(self):
    return self.header[-2]

  def len(self):
    return self.header[-1]

  def data(self) -> bytes:
    return self._data

  def response_bytes_required(self):
    return self.HEADER_SIZE


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


class HBCIresponse(HBCIpacket):
  def __init__(self, payload: bytes):
    self.payload = payload
    self.valid = False
    if len(raw_data) >= 6:
      header = raw_data[:2]
      self.cla = raw_data[2]
      self.ins = raw_data[3]
      self.length = raw_data[4]
      self.payload = payload
      self.crc_received = struct.unpack(self.CHECKSUM_FORMAT, raw_data[-2:])[0]
      calc_crc = self.compute_checksum(raw_data[:-2])
      self.valid = self.crc_received == calc_crc




class HBCIQueryChipID(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x00, ins=0x01)


class HBCISetConfig(HBCIcommand):
  def __init__(self, config_data):
    super().__init__(cla=0x00, ins=0x02, payload=config_data)


class HBCIResetDevice(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x00, ins=0x03)


class HBCIFinalizeFirmware(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x13, ins=0x05)


class HBCIGetStatus(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x00, ins=0x06)


class HBCISelfTest(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x00, ins=0x07)


class HBCIFetchLogs(HBCIcommand):
  def __init__(self):
    super().__init__(cla=0x00, ins=0x08)


class HBCIfirmwareChunk(HBCIcommand):
  def __init__(self, chunk: bytes):
    super().__init__(cla=0x13, ins=0x04, payload=chunk)
#    self.cla = 0x13
#    self.ins = 0x04
#    self.payload = chunk
#    self.length = len(self.payload)
    header = struct.pack(self.HEADER_FORMAT, self.HEADER, self.cla, self.ins)
    length_byte = bytes([self.length])
    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + length_byte + self.payload))
    self._data = header + length_byte + self.payload + crc
    self.retry = 3
    self._status = None
    self._status_sema = from semaphore import CountingCountingSemaphore(0)

  def data(self) -> bytes:
    return self._data

  def response_bytes_required(self) -> int:
    return 8

