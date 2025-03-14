#ifndef MICROPY_HW_BOARD_NAME
// Can be set by mpconfigboard.cmake.
#define MICROPY_HW_BOARD_NAME               "RaptorCore Gen3"
#endif
#define MICROPY_HW_MCU_NAME                 "AUTOBRAKE CAN ULAB LTE"

// Enable UART REPL for modules that have an external USB-UART and don't use native USB.
#define MICROPY_HW_ENABLE_UART_REPL         (1)

#define MICROPY_HW_I2C0_SCL                 (47)
#define MICROPY_HW_I2C0_SDA                 (48)
