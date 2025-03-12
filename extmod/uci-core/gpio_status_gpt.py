import machine

# ESP32-S3 Register Base Addresses (Finalized)
DR_REG_IO_MUX_BASE = 0x60009000  # Correct IO_MUX base for ESP32-S3
DR_REG_GPIO_BASE = 0x60004000    # Base address for GPIO registers
DR_REG_RTC_IO_BASE = 0x60008000  # Base address for RTC GPIO registers

# Corrected Sigma-Delta & RTC_IO_MUX Offsets
SIGMA_DELTA_OFFSET = 0xF00
RTC_IO_MUX_OFFSET = 0x400

class GPIOStatus:
    def __init__(self, pin):
        """
        Initialize the GPIOStatus class with a specific pin number.
        :param pin: GPIO pin number
        """
        self.pin = pin

    def get_status(self):
        """
        Retrieve and display the complete GPIO status including IO_MUX,
        GPIO Matrix, RTC_GPIO, inversion, drive strength, and sigma-delta.
        :return: Dictionary with GPIO status details.
        """
        status = {
            "Pin": self.pin,
            "Mode": self.get_mode(),
            "Pull": self.get_pull(),
            "Level": self.get_level(),
            "Inversion": self.get_inversion(),
            "Drive Strength": self.get_drive_strength(),
            "IO_MUX": self.get_io_mux(),
            "RTC_GPIO": self.get_rtc_gpio(),
            "GPIO Matrix": self.get_gpio_matrix(),
            "Sigma-Delta": self.get_sigma_delta()
        }
        return status

    def get_mode(self):
        """Get GPIO mode by reading the GPIO_FUNCx register."""
        reg_addr = DR_REG_GPIO_BASE + 0x530 + (self.pin * 4)
        reg_value = machine.mem32[reg_addr]

        if reg_value & (1 << 0):
            return "Output"
        elif reg_value & (1 << 1):
            return "Input"
        else:
            return "Unknown Mode"

    def get_pull(self):
        """Check if pull-up or pull-down resistors are enabled using IO_MUX registers."""
        reg_addr = DR_REG_IO_MUX_BASE + (self.pin * 4)
        reg_value = machine.mem32[reg_addr]

        pull_up = reg_value & (1 << 8)
        pull_down = reg_value & (1 << 7)

        if pull_up:
            return "Pull-Up Enabled"
        elif pull_down:
            return "Pull-Down Enabled"
        else:
            return "No Pull Resistors"

    def get_level(self):
        """Get the current logic level of the pin by reading GPIO_IN register."""
        reg_addr = DR_REG_GPIO_BASE + 0x3C  # GPIO_IN register
        reg_value = machine.mem32[reg_addr]

        return "High" if (reg_value & (1 << self.pin)) else "Low"

    def get_inversion(self):
        """Check if the pin signal is inverted via GPIO register."""
        reg_addr = DR_REG_GPIO_BASE + 0x50  # GPIO_FUNCx_IN_SEL_CFG register
        reg_value = machine.mem32[reg_addr + (self.pin * 4)]

        return "Inverted" if reg_value & (1 << 6) else "Not Inverted"

    def get_drive_strength(self):
        """Get the drive strength setting from IO_MUX register."""
        reg_addr = DR_REG_IO_MUX_BASE + (self.pin * 4)
        reg_value = machine.mem32[reg_addr]

        drive_strength = (reg_value >> 4) & 0x3  # Extract drive strength bits
        drive_map = {0: "Weakest", 1: "Weak", 2: "Strong", 3: "Strongest"}
        
        return drive_map.get(drive_strength, "Unknown Drive Strength")

    def get_io_mux(self):
        """Check if the GPIO is configured via IO_MUX or GPIO Matrix."""
        reg_addr = DR_REG_IO_MUX_BASE + (self.pin * 4)
        reg_value = machine.mem32[reg_addr]

        func_sel = (reg_value >> 12) & 0xF  # Extract FUNC_SEL bits

        if func_sel == 0:
            return "GPIO Controlled via IO_MUX"
        else:
            return f"Function {func_sel} assigned (via IO_MUX)"

    def get_rtc_gpio(self):
        """Check if the pin is an RTC GPIO by reading RTC registers."""
        reg_addr = DR_REG_RTC_IO_BASE + RTC_IO_MUX_OFFSET + (self.pin * 4)
        reg_value = machine.mem32[reg_addr]

        if reg_value & (1 << 31):
            return "RTC GPIO Enabled"
        else:
            return "Not an RTC GPIO"

    def get_gpio_matrix(self):
        """Check if the GPIO is using the GPIO Matrix."""
        reg_addr = DR_REG_GPIO_BASE + 0x44  # GPIO_FUNCx_IN_SEL_CFG register
        reg_value = machine.mem32[reg_addr + (self.pin * 4)]

        if reg_value & (1 << 9):
            return "Using GPIO Matrix"
        else:
            return "Direct IO_MUX connection"

    def get_sigma_delta(self):
        """Check if the GPIO is configured for Sigma-Delta modulation."""
        reg_addr = DR_REG_IO_MUX_BASE + SIGMA_DELTA_OFFSET
        reg_value = machine.mem32[reg_addr]

        if reg_value & (1 << self.pin):
            return "Sigma-Delta Enabled"
        else:
            return "Not using Sigma-Delta"


