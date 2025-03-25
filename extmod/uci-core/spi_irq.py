from  machine import SPI, Pin
import struct

_buffsize = 4096



class SPIqueue():
  """ ``Abstract'' base class for SPI IRQ-based communication """
  
  def __init__(self, spi, irq, sync, cs, ce):
    self.spi = spi
    self.irqPin = irq
    self.syncPin = sync
    self.csPin = cs
    self.cePin = ce
    self.sendq[SENDQLEN] = Null
    self.respq[RESPQLEN] = Null
    self.ntfyq[NTFYQLEN] = Null
    self.rxbuffer[RXBUFFLEN] = Null

    # Initialize the IRQ handler
    # self.irqPin.irq(trigger=machine.Pin.IRQ_RISING, handler=self.irq_handler)



  def rd_sync():
    pass

  def rd_handshake():
    pass

  def read(self, length: int):
    self.rd_sync()
    cs.value(0)
    self.rd_handshake()
    spi.read(data)
    cs.value(1)
    self.rd_clear()

  def rd_clear():
    pass




  def wr_sync():
    pass

  def wr_handshake():
    pass

  def write(self, data: bytes):
    self.wr_sync()
    cs.value(0)
    self.wr_handshake()
    spi.write(data)
    cs.value(1)
    self.wr_clear()

  def wr_clear():
    pass


  def irq_handler(self, pin):
    pass



  def _TX_runner():
    pass

  def _RX_runner():
    pass
    

class HBCIqueue(SPIqueue):
  """ SPI Implementation with handshaking for HeliosBoot Control Interface (HBCI) """
  
  def __init__(self, spiQ):
    
    self.cePin.value(0)
    time.sleep(10)
    self.cePin.value(1)


  def _firmware_upload(self):
    f = open(self.firmware, "rb")
    while (chunk := f.read(CHUNKSIZE)):
      packet = HBCIfirmware()
      packet.payload(chunk)
      self.uciq.queue(packet)
      if CHUNKSIZE > len(chunk):
        break

  def rd_handshake():
    # Check if irq is 0 or wait.
    # This is not intended to be the final implementation. Need to block and use irq to detect transition to zero if it isn't zero.
    while 1:
      if self.intPin.value() == 0 :
        break


  def wr_handshake():
    # Check if irq is 0 or wait.
    # This is not intended to be the final implementation. Need to block and use irq to detect transition to zero if it isn't zero.
    while 1:
      if self.irdPin.value() == 0 :
        break

  def irq_handler(self, pin):
    """ Handle IRQ events for HBCI """
    print("HBCI IRQ: Data ready for processing.")





class UCIqueue(SPIqueue):
  """ Unified Communication Interface (UCI) SPI implementation """
  
  def __init__(self):
    pass

  def rd_sync():
    while 0 == self.irqPin.value():
      pass

    self.syncPin.value(1)
    while self.irqPin.value():
      pass

    while self.irqPin.value() == 0:
      pass

  def rd_handshake():
    # Check if irq is 1 or wait. Should already be 1.
    pass

  def rd_clear():
    while irqPin.value:
      pass
    self.syncPin.value(0)


  def wr_handshake():
    pass

  def irq_handler(self, pin):
    pass


#  def read(self, length: int):
#    """ Read from SPI in UCI mode """
#    self.cs.value(0)
#    dummy = bytearray([0x00] * length)
#    response = bytearray(length)
#    self.spi.write_readinto(dummy, response)
#    self.cs.value(1)
#    print(f"UCI Read: {response.hex()}")
#    return response
#
#
#  def write(self, data: bytes):
#    """ Write to SPI in UCI mode """
#    self.cs.value(0)
#    self.spi.write(data)
#    self.cs.value(1)
#    print(f"UCI Write: {data.hex()}")


  def irq_handler(self, pin):
    """ Handle IRQ events for UCI """
    print("UCI IRQ: Data ready for processing.")





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
      return _data[0:-1]


#    def to_bytes(self) -> bytes:
#        payload_size = len(self.payload)
#        header = struct.pack(self.HEADER_FORMAT, self.HEADER)
#        body = struct.pack('>BBH', self.command_id, self.flags, payload_size) + self.payload
#        checksum = self.compute_checksum(header + body)
#        packet = header + body + struct.pack(self.CHECKSUM_FORMAT, checksum)
#        return packet


    def accept_response(self, SPIpacket: header, consume) -> bool:
        """Default response handling (fail safe). Should be overridden."""
        # consume(0)
        return False


    def accept_notification(self, SPIpacket: header, consume) -> bool:
        """Default response handling (fail safe). Should be overridden."""
        # consume(0)
        return False


#    @classmethod
#    def from_bytes(cls, data: bytes):
#        if len(data) < 8:
#            raise ValueError("Data too short for HBCI packet")
#
#        header, = struct.unpack(cls.HEADER_FORMAT, data[0:2])
#        if header != cls.HEADER:
#            raise ValueError("Invalid HBCI header")
#
#        command_id, flags, payload_size = struct.unpack('>BBH', data[2:6])
#        payload = data[6:-2]
#        checksum_received, = struct.unpack(cls.CHECKSUM_FORMAT, data[-2:])
#        checksum_calculated = cls.compute_checksum(data[:-2])
#
#        if checksum_received != checksum_calculated:
#            raise ValueError("Checksum mismatch")
#
#        return cls(command_id, flags, payload)


    @staticmethod
    def compute_checksum(data: bytes) -> int:
        """Simple CRC-16-CCITT"""
        return crc32(data) & 0xFFFF  # Use CRC32 but truncate to 16 bits

    def __repr__(self):
        return f"HBCIPacket(command_id=0x{self.command_id:02X}, flags=0x{self.flags:02X}, payload={self.payload})"




class HBCIpacket(SPIpacket):
  
  HEADER = 0xAA55
  HEADER_FORMAT = '>H'  # Big-endian unsigned short (2 bytes)
  CHECKSUM_FORMAT = '>H'

  def __init__(self):
    pass
    

  def accept_response(self, header, consume):
    pass



class HBCIresponse(HBCIpacket):


  def __init__(self):
    pass


  def hdr():
    pass

  def payload():
    pass

  def crc():
    pass

  def data():
    pass



class HBCIfirmware(SPIpacket):

  def __init__(self):
    pass



#class protocol():
#
#  def __init__():
#
#
#
#
#



class UCI():

  def __init__(self, spi, ce, cs, irq, sync, firmware):

    self.uciq = HBCIqueue(
                   SPI(2, sck=Pin(20), mosi=Pin(8), miso=Pin(19)),
                   ce=Pin(18), cs=Pin(3), irq=Pin(9), sync=Pin(17),
                   firmware = 'H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin'
#                    firmware = 'H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin'
                )





