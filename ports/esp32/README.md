# Micropython CAN/ETH

## Added ulab as submodule in extmod/ulab

## Patched modsocket.c from micropython/micropython commit 611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf

This has been necessary in order to prevent runtime crash when calling `socket.getaddrinfo(...)` when code has been compiled with latest patches of `esp_idf`.
All recent version seem to be affected ie `v5.1`, `5.2`, `5.3`, `5.4`.

[611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf](https://github.com/micropython/micropython/commit/611d8f9ce82ab5e04fb86ab6cfc28d5ed98f33bf) </br>
[Ref](https://github.com/micropython/micropython-esp32/issues/204)</br>
[Ref](https://github.com/micropython/micropython/issues/15841)</br>
[Ref](https://github.com/lvgl-micropython/lvgl_micropython/issues/221)</br>
[Ref](https://github.com/micropython/micropython/pull/16210)</br>

Just as a warning this is not specific to the LAN and will also crashing with attempts to create WLAN socket connections as calling `socket.getaddrinfo(...)` also required.

## Setting Up espresso IDF

assuming using `bash`
in `esp_idf`

```
./install.sh
```
or the following may prevent installing support for unnecessary CPUs.
```
./install.sh esp32
```

in any shells you wish to use for building the firmware.

```
. ~/src/esp/esp_idf/export.sh
```

Adjust parent directories as required based on the location of the idf and micropython sources.

I have been working with v5.2 which seems to be able to compile our old micropython with CAN and W5500 after being patched with the above patch.

I have not been able to compile with v5.3 (compile errors in nimble) and so I have had to redo the duplication o fthe PHY_W5500 as PHY_A2111 which I had previously done with micropython v1.23 or v1.24 and esp-idf v5.3.

It seems there were some changes with esp_eth the w5500 between esp-idf v5.2 and v5.3 as the patches I made from v5.3 didn't seem to work but it was not hard to reproduce the duplication for v5.2 

I have tested the duplicated driver to the point of getting it's IP address via DHCP.
It remains to retarget the duplicate A2111 driver to the associated hardware.

[ORIGINAL README](README%2DMPORIG.md)

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

The above is only required when setting up the micropython environment for the first time.  I have been running it after swapping between `esp_idf` versions but I'm not absolutely sure that is necessary.

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

See [Connect USB devices](https://learn.microsoft.com/en-us/windows/wsl/connect-usb) for alternative ways of installing `usbipd` and a full explanation of the following commands for binding USB devices to WSL.

If not already installed it will be necessary to install `usbipd`

```
winget install --interactive --exact dorssel.usbipd-win
```

It will be necessary to share/bind the USB devices for the com ports with WSL.

```
usbipd list
```

Substitute x-x in the following commands based on the displayed list and desired devices.

```
usbipd bind --busid x-x
```

```
usbipd attach --wsl --busid x-x
```
