from  machine import SPI, Pin
import struct
import time
import threading
from binascii import crc_hqx

_buffsize = 4096


class SPIqueue():
  """ ``Abstract'' base class for SPI IRQ-based communication """

  def __init__(self, spi, irq, sync, cs, ce):
    self.spi = spi
    self.irqPin = irq
    self.syncPin = sync
    self.csPin = cs
    self.cePin = ce
    self.sendq = []
    self.respq = []
    self.ntfyq = []
    self.rxbuffer = bytearray()
    self.rx_sema = threading.Semaphore(0)
    self.tx_sema = threading.Semaphore(0)
    self.buffer_lock = threading.Lock()

    threading.Thread(target=self._sendq_runner, daemon=True).start()
    threading.Thread(target=self._respq_runner, daemon=True).start()

  def rd_sync():
    pass

  def rd_handshake():
    pass

  def read(self, length: int):
    self.rd_sync()
    self.csPin.value(0)
    self.rd_handshake()
    self.spi.read(length)
    self.csPin.value(1)
    self.rd_clear()

  def rd_clear():
    pass

  def wr_sync():
    pass

  def wr_handshake():
    pass

  def write(self, data: bytes):
    self.wr_sync()
    self.csPin.value(0)
    self.wr_handshake()
    self.spi.write(data)
    self.csPin.value(1)
    self.wr_clear()

  def wr_clear():
    pass

  def irq_handler(self, pin):
    pass

  def _sendq_runner(self):
    """Continuously transmit packets from the send queue."""
    while True:
      self.tx_sema.acquire()
      if not self.sendq:
        continue

      packet = self.sendq.pop(0)
      data = packet.data()
      self.write(data)

      if packet.response_bytes_required() > 0:
        self.respq.append(packet)
      elif packet.notify_bytes_required() > 0:
        self.ntfyq.append(packet)

      print(f"Transmitted: {data.hex()}")

  def _respq_runner(self):
    """Process incoming data in rxbuffer, using semaphore to block until enough data is available."""
    while True:
      self.rx_sema.acquire()

      with self.buffer_lock:
        if not self.respq:
          continue

        packet = self.respq[0]
        needed = packet.response_bytes_required()

        if len(self.rxbuffer) < needed:
          continue

        def consume(n):
          while True:
            with self.buffer_lock:
              if len(self.rxbuffer) >= n:
                result = self.rxbuffer[:n]
                del self.rxbuffer[:n]
                return result
            time.sleep(0.001)

        header = self.rxbuffer[:needed]
        if packet.accept_response(header, consume):
          self.respq.pop(0)

  def append_rx_data(self, data: bytes):
    with self.buffer_lock:
      self.rxbuffer.extend(data)
      self.rx_sema.release()

  def queue_packet(self, packet):
    self.sendq.append(packet)
    self.tx_sema.release()


class HBCIqueue(SPIqueue):
  def __init__(self, spiQ: SPIqueue):
    super().__init__(spiQ.spi, spiQ.irqPin, spiQ.syncPin, spiQ.csPin, spiQ.cePin)
    self.cePin.value(0)
    time.sleep(10)
    self.cePin.value(1)

  def _firmware_upload(self):
    f = open(self.firmware, "rb")
    while (chunk := f.read(CHUNKSIZE)):
      packet = HBCIfirmware()
      packet.payload(chunk)
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


class SPIpacket(bytes):
  self.hdr[HDRLEN] = 0
  self.retry = 3
  self.respLen = 0
  self.ntfyLen = 0
  self._data = Null

  def __init__(self, command_id: int, flags: int, payload: bytes = b''):
    self.command_id = command_id
    self.flags = flags
    self.payload = payload

  def hdr(self, data=Null):
    pass

  def payload(self, data=Null):
    _data[-len(data)-2] = data
    return self._data[:-2]

  def crc(self):
    return _data[-2:-1]

  def data(self) -> bytes:
    return self._data[0:-1]

  def response_bytes_required(self) -> int:
    return 0

  def notify_bytes_required(self) -> int:
    return 0

  def accept_response(self, header, consume) -> bool:
    return False

  def accept_notification(self, header, consume) -> bool:
    return False

  @staticmethod
  def compute_checksum(data: bytes) -> int:
    return crc_hqx(data, 0xFFFF)

  def __repr__(self):
    return f"HBCIPacket(command_id=0x{self.command_id:02X}, flags=0x{self.flags:02X}, payload={self.payload})"


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
    header = struct.pack(self.HEADER_FORMAT, self.HEADER, cla, ins, len(self.payload))

    crc = struct.pack(self.CHECKSUM_FORMAT, self.compute_checksum(header + payload))
    self._data = header + payload + crc

  def data(self) -> bytes:
    return self._data

  def minimum_resp_len(self) -> int:
    return len(self.header)


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


class HBCIfirmware(SPIpacket):
  def __init__(self):
    pass


class UCI():
  def __init__(self, spi, ce, cs, irq, sync, firmware):
    self.uciq = HBCIqueue(
      SPI(2, sck=Pin(20), mosi=Pin(8), miso=Pin(19)),
      ce=Pin(18), cs=Pin(3), irq=Pin(9), sync=Pin(17),
      firmware='H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin'
    )

