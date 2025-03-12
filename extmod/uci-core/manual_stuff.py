# UciManager

from uci_manager import UciManager


uci = UciManager('/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin')


uci = UciManager('/H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin')


# UciCorDriverSPI
from uci_core import UciCoreiDriverSPI

uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_MAINLINE_PROD_FW_46.41.06_0052bbfed983a1f1.bin') 

uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin', sck=20, mosi=0, miso=19, cs=3, ce=18, irq=9)

uci = UciCoreDriverSPI(2, '/H1_IOT.SR150_FACTORY_PROD_FW_46.41.06_0052bbfed983a1f1.bin', sck=8, mosi=20, )


# These should create output on respective pins
from machine import Pin, PWM 

pwm20 = PWM(Pin(20), freq=500, duty=512)
pwm19 = PWM(Pin(19), freq=500, duty=512)
pwm8 = PWM(Pin(8), freq=500, duty=512)


pwm20.deinit()
pwm19.deinit()
pwm8.deinit()

