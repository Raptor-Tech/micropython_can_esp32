## New testing stuff
```

from machine import Pin, SPI
from spi import SPIqueue
from hbci import HBCIqueue

```

```

spi = SPI(2, sck=Pin(20), mosi=Pin(8), miso=Pin(19))

sQ = SPIqueue( spi=spi, ce=Pin(10), cs=Pin(3), irq=Pin(9), sync=Pin(18), firmware='H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin')

hQ = HBCIqueue(sQ)

```

```
def status():
  print(f"ce:{ce.value()} cs:{cs.value()} sck:{sck.value()} sdo:{sdo.value()} irq:{irq.value()} sdi:{sdi.value()} sync:{sync.value()}")



ce = Pin(18, Pin.OUT)
cs = Pin(3, Pin.OUT)
sck = Pin(20,Pin.OUT)
sdo = (miso := Pin(19, Pin.IN))
irq = Pin(9,Pin.IN)
sdi = (mosi := Pin(8,Pin.OUT))
sync = Pin(17,Pin.OUT)

ce.value(0)
cs.value(1)
sck.value(0)
sdi.value(0)
sync.value(0)
sleep(1)
status()

# Old Test Stuff

```

sr150 = SR150(SPI(2, sck=Pin(20), mosi=Pin(8), miso=Pin(19)), cs=Pin(3), ce=Pin(10), irq=Pin(9))

sr150 = SR150(SPI(2, sck=Pin(20), mosi=Pin(19), miso=Pin(8)), cs=Pin(3), ce=Pin(10), irq=Pin(9))

#sr150.upload_firmware('H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
#sr150.upload_firmware('/H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
```
## UciManager

```
from uci_manager import UciManager
```


```
uci = UciManager('/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
```


```
uci = UciManager('/H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin')
```


## UciCorDriverSPI
```
from uci_core import UciCoreiDriverSPI
```

```
uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin') 
```

```
uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin', sck=20, mosi=0, miso=19, cs=3, ce=18, irq=9)
```

```
uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin', sck=8, mosi=20, )
```


## These should create output on respective pins
```
from machine import Pin, PWM 
```

```
pwm20 = PWM(Pin(20), freq=500, duty=512)
pwm19 = PWM(Pin(19), freq=500, duty=512)
pwm8 = PWM(Pin(8), freq=500, duty=512)
```


```
pwm20.deinit()
pwm19.deinit()
pwm8.deinit()
```



