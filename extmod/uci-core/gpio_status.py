
class gpioStatus:

  # 
  MINPOW2 = staticmethod(lambda x: (mp2 := lambda m: (m > 1)*(mp2(m>>1)+1))(x)) 

  BITMASK = staticmethod(lambda a, b: (((2<<(a-b))-1)<<b))

  MASKGETVAL = staticmethod(lambda m,x: ((x & m) >> gpioStatus.MINPOW2(m)))
  MASKSETVAL = staticmethod(lambda m,x: ((x << gpioStatus.MINPOW2(m)) & m))

  # GPIO Base Table 4.3-3 Ch 4.3.5.1 pp.408--409  

  GPIO_BASE = 0x60004000
  LP_MGMT = 0x60008000    # Base
  IO_MUX = 0x60009000

  # GPIO Matrix Registers Ch 6.14.1 pp.496--497

  # p.496
  GPIO_BT_SELECT_REG = 0x00
  GPIO_OUT_REG = 0x4
  GPIO_OUT_W1TS_REG = 0x8
  GPIO_OUT_W1TC_REG = 0xC
  GPIO_OUT1_REG = 0x10
  GPIO_OUT1_W1TS_REG = 0x14
  GPIO_OUT1_W1TC_REG = 0x18
  GPIO_SDIO_SELECT_REG = 0x1C
  GPIO_ENABLE_REG = 0x20
  GPIO_ENABLE_W1TS_REG = 0x24
  GPIO_ENABLE_W1TC_REG = 0x28
  GPIO_ENABLE1_REG = 0x2C
  GPIO_ENABLE1_W1TS_REG = 0x30
  GPIO_ENABLE1_W1TC_REG = 0x34
  GPIO_STRAP_REG = 0x38

  # p.497
  GPIO_IN_REG = 0x3C
  GPIO_IN1_REG = 0x40
  GPIO_PINn_REG = staticmethod(lambda n: ((n>=0)*(n<49)*(n*4+0x74)))  # 0 -- 48
  GPIO_FUNCn_IN_SEL_CFG = staticmethod(lambda n: ((n>=0)*(n<=255)*(n*4+0x154))) # 0 -- 255
  GPIO_FUNCn_OUT_SEL_CFG = staticmethod(lambda n: ((n>=0)*(n<=48)*(n*4+0x554))) # 0 -- 48
  GPIO_CLOCK_GATE_REG = 0x62C

  GPIO_STATUS_REG = 0x44
  GPIO_STATUS1_REG = 0x50
  GPIO_CPU_INT_REG = 0x5C
  GPIO_CPU_MNI_INT_REG = 0x60
  GPIO_CPU_INT1_REG = 0x68
  GPIO_CPU_MNI_INT1_REG = 0x6C

  GPIO_STATUS_W1TS_REG = 0x48
  GPIO_STATUS_W1TC_REG = 0x4C
  GPIO_STATUS1_W1TS_REG = 0x54
  GPIO_STATUS1_W1TC_REG = 0x58

  GPIO_STATUS_NEXT_REG = 0x14C
  GPIO_STATUS_NEXT1_REG = 0x150

  GPIO_DATE_REG = 0x6cf


  # IO_MUX + REG [Tech Ref] pp.496--498

  IO_MUX_PIN_CNTL_REG = 0x00
  IO_MUX_GPIOn_REG = staticmethod(lambda n: (((n>=0) and (N<=48))*(n*4+0x4)))   # This agrees with table p.498 formula (n*4+0x10) from p.514 appears to be incorrect.
  #IO_MUX_GPIOn_REG = lambda n: (n*4+0x10)  # This is the formula given in [Tech Ref] p.514 but this disagrees with the table p.498

  IO_MUX_MCU_OE = BITMASK(0,0)
  IO_MUX_SLP_SEL = BITMASK(1,1)
  IO_MUX_MCU_WPD = BITMASK(2,2)
  IO_MUX_MCU_WPU = BITMASK(3,3)
  IO_MUX_MCU_IE = BITMASK(4,4)
  IO_MUX_MCU_DRV = BITMASK(6,5)
  IO_MUX_FUN_WPD = BITMASK(7,7)
  IO_MUX_FUN_WPU = BITMASK(8,8)
  IO_MUX_FUN_IE = BITMASK(9,9)
  IO_MUX_FUN_DRV = BITMASK(11,10)
  IO_MUX_FUN_SEL = BITMASK(14,12)
  IO_MUX_FILTER_EN = BITMASK(15,15)
  IO_MUX_RES31 = BITMASK(31,16)

  # Ch 6.14.3 p.499
  #GPIOBASE + 0xf00 + ...REG

  GPIO_SIGMADELTAn_REG = staticmethod(lambda n: (((n>=0) and (n<=7))*(n*4+0x0))) # 0 -- 7
  GPIO_SIGMADELTA_CG_REG = 0x20
  GPIO_SIGMADELTA_CG_MISC = 0x24
  GPIO_SIGMADELTA_CG_VERSION = 0x28

  # IO_MUX [Tech Ref] p.501 Ch6.15.1
  GPIOn_OUT_DATA = staticmethod(lambda n: (((n>=0) and (n<=25))*(1 << (n+n//22*4))))  # n = [0,26] -> [0,21],[26,31]
  #GPIOn_OUT_W1 = lambda x: (1<<x) 
  GPIOn_OUT_W1 = staticmethod(lambda x: gpioStatus.GPIOn_OUT_DATA(x))

  GPIOn_OUT1_DATA = staticmethod(lambda n: ((n>=32) and (n<=48))*(1 << (n-32+22)))
  GPIOn_OUT1_W1 = staticmethod(lambda x: gpioStatus.GPIOn_OUT1_DATA(x))

  # IO MUX Registers
  # IO_MUX [Tech Ref] p.513 Ch6.15.2


  # Registers RTC IO MUX
  # LP_MGMT + 0x400 + REG [Tech Ref] pp.516--525 Ch6.15.4

  RTC_GPIO_OUT_REG = 0x0
  RTC_GPIO_OUT_W1TS_REG = 0x4
  RTC_GPIO_OUT_W1TC_REG = 0x8
  RTC_GPIO_ENABLE_REG = 0x0c
  RTC_GPIO_ENABLE_W1TS_REG = 0x10
  RTC_GPIO_ENABLE_W1TC_REG = 0x14
  RTC_GPIO_STATUS_REG = 0x18
  RTC_GPIO_STATUS_W1TS = 0x1c
  RTC_GPIO_STATUS_W1TC = 0x20
  RTC_GPIO_IN_REG = 0x24
  RTC_GPIO_PINn_REG = staticmethod(lambda n: (((n>=0) and (n<=21))*(0x28+4*n)))        # 0 -- 21
  RTC_IO_TOUCH_PADn_REG = staticmethod(lambda n: (((n>=0) and (n<=14))*(0x84+4*n)))    # 0 -- 14
  RTC_IO_XTAL_32P_PAD = RTC_IO_TOUCH_PADn_REG(15) # 15
  RTC_IO_XTAL_32N_PAD = RTC_IO_TOUCH_PADn_REG(16) # 16
  RTC_IO_RTC_PADn_REG = staticmethod(lambda n: (((n>=17) and (n<=21))*(0x84+4*n)))      # 17 -- 21

  # Databits and Bitmasks
  RTC_GPIOn_OUT_DATA = staticmethod(lambda n: (((n>=0) and (n<=21))*(1 << (n+10))))  # n = [21,0] -> [31,10]
  RTC_GPIOn_OUT_W1 = staticmethod(lambda x: RTC_GPIOn_OUT_DATA(x))
  RTC_GPIOn_ENABLE_DATA = staticmethod(lambda x: RTC_GPIOn_OUT_DATA(x))
  RTC_GPIOn_ENABLE_W1 = staticmethod(lambda x: RTC_GPIOn_ENABLE_DATA(x))
  RTC_GPIOn_STATUS_DATA = staticmethod(lambda x: RTC_GPIOn_OUT_DATA(x))
  RTC_GPIOn_STATUS_W1 = staticmethod(lambda x: RTC_GPIOn_STATUS_DATA(x))
  RTC_GPIOn_IN_NEXT = staticmethod(lambda x: RTC_GPIOn_IN_DATA(x))

  RTC_GPIO_PIN_PAD_DRIVER = BITMASK(2,2)
  RTC_GPIO_PIN_INT_TYPE = BITMASK(9,7)
  RTC_GPIO_PIN_WAKEUP_ENABLE = BITMASK(10,10)


  # [Tech Ref] pp.516--525 Ch6.15.4   LP_MGMT+0x400
  RTC_IO_MUX_GPIOn_REG = staticmethod(lambda n: (n*4+0x4))  # 

  RTC_IO_RTC_GPIOn_REG = staticmethod(lambda n: (((n>=17) and (N<=21))*(n*4+0x4)))  # 
  #RTC_IO_MUX_GPIO17 = 0xC8
  #RTC_IO_MUX_GPIO18 = 0xCC
  #RTC_IO_MUX_GPIO19 = 0xD0
  #RTC_IO_MUX_GPIO20 = 0xD4
  #RTC_IO_MUX_GPIO21 = 0xD8

  # RTC_IOMUX...

  # These are the same registers.
  # [Tech Ref] p.584 Ch10.7 Registers at offset from LP_MGMT + 0x0
  # [Tech Ref] pp.587--633 Ch10.8 Registers at offset from LP_MGMT + 0x0


  RTC_CNTL_TOUCH_PAD_HOLD_REG = 0xD8  # p.585 p.620

  pin = 0

  def __init__(self, pin):
    self.pin = pin;
    self.RTS_GPIO_OUT_SC_MASK = self.RTC_GPIOn_ENABLE_DATA(self.pin)
    self.RTS_GPIO_OUT_RD_MASK = self.RTC_GPIOn_ENABLE_DATA(self.pin)
    self.RTS_GPIO_ENABLE_SC_MASK = self.RTC_GPIOn_ENABLE_W1(self.pin)
    self.RTS_GPIO_ENABLE_RD_MASK = self.RTC_GPIOn_ENABLE_DATA(self.pin)
    self.RTS_GPIO_STATUS_SC_MASK = self.RTC_GPIOn_ENABLE_W1(self.pin)
    self.RTS_GPIO_STATUS_RD_MASK = self.RTC_GPIOn_ENABLE_DATA(self.pin)

  def _reg(self, addr, value):
    pass

  def _reg_RTC_GPIO_OUT_DATA(self):
    ADDR = self.LP_MGMT+self.RTC_GPIO_OUT_DATA_REG
    return MASKGETVAL(self.PTC_GPIOn_OUT_RD_MASK, machine.mem32[ADDR])

  def _reg_RTC_GPIO_OUT_W1TS(self):
    ADDRSET = self.LP_MGMT + self.RTC_GPIO_OUT_W1TS_REG
    machine.mem32[ADDRSET] = self.RTS_GPIO_OUT_SC_MASK
    return self._reg_RTC_GPIO_OUT_DATA()

  def _reg_RTC_GPIO_OUT_W1TC(self):
    ADDRRST = self.LP_MGMT + self.RTC_GPIO_OUT_W1TC_REG
    machine.mem32[ADDRRST] = self.RTS_GPIO_OUT_SC_MASK
    return self._reg_RTC_GPIO_OUT_DATA()


  def _reg_RTC_GPIO_ENABLE(self):
    ADDR = self.LP_MGMT + self.RTC_GPIO_OUT_DATA_REG
    return MASKGETVAL(self.PTD_GPIOn_ENABLE_DATA(self.pin),machine.mem32[ADDR])

  def _reg_RTC_GPIO_ENABLE_W1TS(self):
    ADDRSET = LP_MGMT + self.RTC_GPIO_ENABLE_W1TS_REG
    machine.mem32[ADDRSET] = self.RTC_GPIO_ENABLE_SR_MASK
    return self._reg_RTC_GPIO_OUT_DATA()

  def _reg_RTC_GPIO_ENABLE_W1TC(self):
    ADDRRST = self.LP_MGMT+self.RTC_GPIO_OUT_DATA_REG
    machine.mem32[ADDRRST] = self.RTC_GPIO_ENABLE_SR_MASK
    return self._reg_RTC_GPIO_OUT_DATA()


  def _reg_RTC_GPIO_STATUS(self):
    ADDR = self.LP_MGMT+self.RTC_GPIO_STATUS_REG
    return MASKGETVAL(self.PTC_GPIO_STATUS_SR_MASK,machine.mem32[ADDR])

  def _reg_RTC_GPIO_STATUS_W1TS(self):
    ADDRSET = self.LP_MGMT+self.RTC_GPIO_STATUS_W1TS_REG
    machine.mem32[ADDRSET] = self.RTC_GPIO_STATUS_SR_MASK
    return self._reg_RTC_GPIO_STATUS_REG()

  def _reg_RTC_GPIO_STATUS_W1TC(self):
    ADDRSET = LP_MGMT+RTC_GPIO_STATUS_W1TC_REG
    machine.mem32[ADDRSET] = RTC_GPIO_STATUS_SR_MASK
    return self._reg_RTC_GPIO_OUT_DATA()


  def gpio_set(self):
    pass

  def gpio_rst(self):
    pass

  def display(self):
    pass

  def _disp_IO_MUX(self):
    pass
   
  def _disp_GPIO(self):
    pass

  def _disp_RTC_GPIO(self):
    pass


