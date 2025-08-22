#ifndef MICROPY_HW_BOARD_NAME
// Can be set by mpconfigboard.cmake.
#define MICROPY_HW_BOARD_NAME               "Ultra-WideBand Gen0"
#endif
#define MICROPY_HW_MCU_NAME                 "UWB0.0"
#define MICROPY_HW_USB_CDC                  (0)
#define MICROPY_HW_ENABLE_USBDEV            (0)
// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)
//#define MICROPY_HW_I2C0_SCL                 (14)
//#define MICROPY_HW_I2C0_SDA                 (2)
#define MICROPY_HW_TWAI_TX  (5)
#define MICROPY_HW_TWAI_RX  (4)

