# SPIqueue Base Layer
# Provides transport abstraction and state context for HBCI and UCI layers.
# Handles TX/RX queues, threading, semaphores, and ring buffering.
# Protocol-specific behavior is implemented by subclasses.

from  machine import SPI, Pin
import struct
import time
import _thread

_buffsize = 4096


class SPIqueue():
  """ ``Abstract'' base class for SPI IRQ-based communication """

  def __init__(self, spi, ce, cs, irq, sync, firmware=None):
    self.spi = spi
    self.csPin = cs
    self.cePin = ce
    self.irqPin = irq
    self.syncPin = sync
    self.firmware = firmware

    self.sendq = []
    self.respq = []
    self.ntfyq = []
    self.rxbuffer = bytearray()
    self.rx_sema = # Unsupported in MicroPython - implement custom semaphore(0)
    self.tx_sema = # Unsupported in MicroPython - implement custom semaphore(0)
    self.buffer_lock = _thread.allocate_lock()

    _thread.start_new_thread(self._sendq_runner, ())
    _thread.start_new_thread(self._respq_runner, ())
    
    return self

  def rd_sync(self):
    pass

  def rd_handshake(self):
    pass

  def read(self, length: int):
    self.rd_sync()
    self.csPin.value(0)
    self.rd_handshake()
    self.spi.read(length)
    self.csPin.value(1)
    self.rd_clear()

  def rd_clear(self):
    pass

  def wr_sync(self):
    pass

  def wr_handshake(self):
    pass

  def write(self, data: bytes):
    self.wr_sync()
    self.csPin.value(0)
    self.wr_handshake()
    self.spi.write(data)
    self.csPin.value(1)
    self.wr_clear()

  def wr_clear(self):
    pass

  def irq_handler(self, pin):
    pass

  def _sendq_runner(self):
    """Process packets from the send queue. Wait for ACK if response is expected."""
    while True:
      self.tx_sema.acquire()
      if not self.sendq:
         continue

      packet = self.sendq[0]  # peek without removing
      data = packet.data()
      self.write(data)

      if packet.response_bytes_required() > 0:
        try:
          result = packet.status(timeout=1.0)
        except TimeoutError:
          print("⏱️", end="")
          packet.retry -= 1
          if packet.retry > 0:
            packet._status = None
            self.tx_sema.release()
          else:
            print("Dropping after timeout retries.")
            self.sendq.pop(0)
          continue

        if result == "ACK":
          print("✅", end="")
          self.sendq.pop(0)
        elif result == "RETRY":
          print("🔁", end="")
          time.sleep(0.05)
          self.tx_sema.release()
        elif result == "FAIL":
          print("❌")
          self.sendq.pop(0)
        continue

      print("")


      if packet.notify_bytes_required() > 0:
        self.ntfyq.append(packet)

      print("")
      

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
  hdr = bytearray()
  retry = 3
  respLen = 0
  ntfyLen = 0
  _data = bytearray()

  def __init__(self, command_id: int, flags: int, payload: bytes = b''):
    self.command_id = command_id
    self.flags = flags
    self.payload = payload
    self._status = None
    self._status_sema = # Unsupported in MicroPython - implement custom semaphore(0)

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

  def hdr(self, data=None):
    return None

  def payload(self, data=None):
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
    return crc_16(data)

  def __repr__(self):
    return f"HBCIPacket(command_id=0x{self.command_id:02X}, flags=0x{self.flags:02X}, payload={self.payload})"

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
