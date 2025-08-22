set(IDF_TARGET esp32)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    ${SDKCONFIG_IDF_VERSION_SPECIFIC}
    boards/sdkconfig.240mhz
    boards/sdkconfig.ble
    boards/sdkconfig.spiram
    boards/sdkconfig.spiram_sx
    boards/ESP32_UWB_GEN0/sdkconfig.board
)

if(MICROPY_BOARD_VARIANT STREQUAL "SPIRAM_OCT")
    set(SDKCONFIG_DEFAULTS
        ${SDKCONFIG_DEFAULTS}
        boards/sdkconfig.240mhz
        boards/sdkconfig.spiram_oct
    )

    list(APPEND MICROPY_DEF_BOARD
	    MICROPY_HW_BOARD_NAME="ESP32_UWB_GEN0"
    )
endif()
