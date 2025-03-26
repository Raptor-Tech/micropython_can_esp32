from  machine import SPI, Pin
import struct
import time
import _thread
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
    """Process packets from the send queue. Wait for ACK if response is expected."""
      self.tx_sema.acquire()
      if not self.sendq:
        continue

      packet = self.sendq[0]  # peek without removing
      data = packet.data()
      self.write(data)

      if packet.response_bytes_required() > 0:
        self.respq.append(packet)

      if packet.response_bytes_required() > 0:
        try:
          result = packet.status(timeout=1.0)
        except TimeoutError:
          print("⏱️ Timeout waiting for response")
          packet.retry -= 1
          if packet.retry > 0:
            packet._status = None
            self.tx_sema.release()
          else:
            print("❌ Dropping after timeout retries.")
            self.sendq.pop(0)
          continue

        if result == "ACK":
          print("✅ ACK received")
          self.sendq.pop(0)
        elif result == "RETRY":
          print("🔁 Retrying")
          time.sleep(0.05)
          self.tx_sema.release()
        elif result == "FAIL":
          print("❌ Failed, dropping packet")
          self.sendq.pop(0)
        continue

      if result == "ACK":
        print("✅ ACK received")
        self.sendq.pop(0)
      elif result == "RETRY":
        print("🔁 Retrying")
        time.sleep(0.05)
        self.tx_sema.release()
      elif result == "FAIL":
        print("❌ Failed, dropping packet")
        self.sendq.pop(0)

      if packet.notify_bytes_required() > 0:
        self.ntfyq.append(packet)

  def _respq_runner(self):
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

        header_chk = self.rxbuffer[:needed]
        if packet.accept_response(header_chk, consume):
          self.respq.pop(0)

  def append_rx_data(self, data: bytes):
    with self.buffer_lock:
      self.rxbuffer.extend(data)
      self.rx_sema.release()

  def queue_packet(self, packet):
    self.sendq.append(packet)
    self.tx_sema.release()



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
    self._status = None
    self._status_sema = threading.Semaphore(0)

  def status(self, timeout=1.0):
    if self._status is not None:
      return self._status
    if timeout == 0:
      return None
    if not self._status_sema.acquire(timeout=timeout):
      raise TimeoutError("Packet status wait timed out")
    return self._status

  def set_status(self, value):
    self._status = value
    self._status_sema.release()

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


