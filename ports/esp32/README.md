# Micropython CAN/ETH

## Added ulab as submodule in extmod/ulab

## Patched modsocket.c from micropython/micropython commit 611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf

This has been necessary in order to prevent runtime crash when calling `socket.getaddrinfo(...)` when code has been compiled with latest patches of `esp_idf`.
All recent version seem to be affected ie `v5.1`, `5.2`, `5.3`, `5.4`.

[611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf](https://github.com/micropython/micropython/commit/611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf) </br>
(https://github.com/micropython/micropython-esp32/issues/204)</br>
(https://github.com/micropython/micropython/issues/15841)</br>
(https://github.com/lvgl-micropython/lvgl_micropython/issues/221)</br>
(https://github.com/micropython/micropython/pull/16210)</br>


## Building

Espressif IDF `esp_idf` is in `~/src/esp/esp_idf`

Micropython code is in `~/src/esp/micropython_can_esp32`

In `mpy-cross`
```
make
```

could also be done with:
```
make -C mpy-cross
```
from repository root or

```
make -C ../../mpy-cross
```
from `ports/esp32` or

```
make -C ~/src/esp/micropython_can_esp32/mpy-cross
```

from anywhere

In `ports/esp32`
```
make BOARD=ESP32_GENERIC_S3 MICROPY_FLOAT_IMPL=MICORPY_FLOAT_IMPL_DOUBLE USER_C_MODULE=~/src/esp/micropython_can_esp32/extmod/ulab  V=1 submodules
```
```
make BOARD=ESP32_GENERIC_S3 MICROPY_FLOAT_IMPL=MICORPY_FLOAT_IMPL_DOUBLE USER_C_MODULE=~/src/esp/micropython_can_esp32/extmod/ulab  V=1
```
The path to the `USER_C_MODULE` need to be absolute as it seems to be being called from different levels in the build heirachy. 
Thus the above commends may need adjusting dependent on where the code is cloned.  There may be a variable assigned to the project root
which could be used to avoid the need for adjusting the above commands.

## Flashing

```
python3 -m esptool -p /dev/ttyUSB1 erase_flash
```

```
python3 -m esptool -p /dev/ttyUSBX write_flash 0x0 build-ESP32_GENERIC_S3/bootloader.bin 0x8000 build-ESP32_GENERIC_S3/partition_table/partition-table.bin 0x10000 build-ESP32_GENERIC_S3/micropython.bin
```

replace `ttyUSBX` with `ttyUSB0`, `ttyUSB1`, `ttyUSB2`, `ttyUSB3` or other as is appropriate.

## WSL

It will be necessary to share/bind the USB devices for the com ports with WSL.

```
usbipd list
```

```
usbipd bind --busid x-x
```

```
usbipd attach --wsl --busid x-x
```
