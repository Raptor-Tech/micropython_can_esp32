import machine

# ESP32-S3 USB Peripheral Register Base Addresses
DR_REG_USB_SERIAL_JTAG_BASE = 0x60038000  # USB Serial/JTAG base
DR_REG_USB_EXTERNAL_REG_BASE = 0x60039000  # USB Serial/JTAG base
DR_REG_USB_OTG_BASE = 0x60080000          # USB OTG base
DR_REG_IO_MUX_BASE = 0x60009000           # IO_MUX base

# USB Register Offsets
USB_SERIAL_JTAG_CONF0 = DR_REG_USB_SERIAL_JTAG_BASE + 0x18
USB_OTG_CONF = DR_REG_USB_OTG_BASE + 0x100
USB_OTG_PD_CTRL = DR_REG_USB_OTG_BASE + 0x110

# USB DP/DM GPIO Pins (Default: GPIO19 = D-, GPIO20 = D+)
USB_DP_PIN = 20
USB_DM_PIN = 19

class USBControl:
    @staticmethod
    def disable_usb_serial_jtag():
        """Disable USB Serial/JTAG function."""
        machine.mem32[USB_SERIAL_JTAG_CONF0] |= (1 << 0)  # Disable JTAG
        machine.mem32[USB_SERIAL_JTAG_CONF0] &= ~((1 << 14)|(1 << 9))  # Disable JTAG
    
    @staticmethod
    def disable_usb_otg():
        """Disable USB OTG function."""
        machine.mem32[USB_OTG_CONF] |= (1 << 18)  # Disable USB_OTG Core Clock
        machine.mem32[USB_OTG_PD_CTRL] |= (1 << 0)  # Power down USB_OTG

    @staticmethod
    def disable_usb_pins():
        """Disable USB DP/DM functionality in IO_MUX."""
        dp_reg = DR_REG_IO_MUX_BASE + (4+USB_DP_PIN * 4)
        dm_reg = DR_REG_IO_MUX_BASE + (4+USB_DM_PIN * 4)
        machine.mem32[dp_reg] &= ~((1 << 9)&(1<<14))  # Reset function
        machine.mem32[dm_reg] &= ~(1 << 9)

    @staticmethod
    def disable_all_usb():
        """Disable all USB functions (Serial JTAG, OTG, IO_MUX)."""
        USBControl.disable_usb_serial_jtag()
        USBControl.disable_usb_otg()
#        USBControl.disable_usb_pins()
        print("✅ USB Functions Disabled!")

# Example usage:
#USBControl.disable_all_usb()

