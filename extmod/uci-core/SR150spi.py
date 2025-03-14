import machine, time

# Configure SPI using the given pins:
spi = machine.SPI(1,
                  baudrate=2000000,  # Adjust baudrate as needed
                  polarity=0,
                  phase=0,
                  sck=machine.Pin(20),
                  mosi=machine.Pin(8),
                  miso=machine.Pin(19))

# Configure control pins: CS (chip select), CE (chip enable), IRQ (interrupt)
cs  = machine.Pin(3, machine.Pin.OUT)
ce  = machine.Pin(10, machine.Pin.OUT)
irq = machine.Pin(9, machine.Pin.IN)

# Make sure CS is inactive (high) and CE is low to begin with
cs.value(1)
ce.value(0)

class SR150:
    def __init__(self, spi, cs, ce, irq):
        self.spi = spi
        self.cs = cs
        self.ce = ce
        self.irq = irq
        self.response_buffer = bytearray(256)  # Buffer to store received data
        self.data_ready = False  # Flag to indicate data readiness
        self.irq_enabled = False  # Flag to track IRQ state

        # Configure IRQ pin for rising edge interrupt
        self.irq.irq(trigger=machine.Pin.IRQ_RISING, handler=self.irq_handler)

    def irq_handler(self, pin):
        """
        IRQ handler function. This is triggered when the IRQ pin is high (data is ready).
        It resumes data receiving from the SPI interface.
        """
        if not self.irq_enabled:
            return  # Avoid unnecessary triggering if IRQ handling is disabled
        
        print("IRQ: Data ready to be received.")
        self.receive_data()

    def send_command(self, cmd, payload=b''):
        """
        Send a UCI command packet over SPI.
        For simplicity, we assume the packet format is:
          [Header (4 bytes)] + [payload]
        """
        # Example header based on assumed command structure
        header = bytearray([0x00, 0x00, 0x00, 0x00])  # Replace with actual header fields
        packet = header + payload
        self.cs.value(0)
        self.spi.write(packet)  # Send command to the device
        self.cs.value(1)

    def read_response(self, length=256):
        """
        Read a response from the SPI interface, sending idle (zero) bytes while waiting.
        We continue sending zeros until the device becomes idle.
        """
        print("Reading response...")

        # Reset the response buffer
        self.response_buffer = bytearray(length)

        # Enable IRQ so we can receive data asynchronously
        self.irq_enabled = True
        self.data_ready = False  # Reset the flag

        # Wait until we receive all the expected data
        while not self.data_ready:
            # Keep sending zero bytes while waiting for data
            self.cs.value(0)
            self.spi.write(b'\x00')  # Send zero byte to keep the interface alive
            self.cs.value(1)
            time.sleep_ms(10)  # Adjust the delay if necessary

        # Disable IRQ after receiving data
        self.irq_enabled = False
        print("Response received:", self.response_buffer)

        return self.response_buffer

    def receive_data(self):
        """
        This function is called by the IRQ handler to receive data from the SPI interface.
        It reads the data from SPI while the device is active and ready to send data.
        """
        self.cs.value(0)
        # Read 1 byte from the SPI bus while the device sends data
        byte = self.spi.read(1)
        if byte:
            # Store the received byte in the response buffer
            self.response_buffer.append(byte[0])
        self.cs.value(1)

        # Check if we have completed receiving data (e.g., if the device signals the end)
        # You may implement more sophisticated checks to determine if the device is idle.
        if len(self.response_buffer) > 0 and byte == b'\x00':  # Example: check for idle byte
            self.data_ready = True
            print("Data stream idle, stopping.")
        
    def reset_device(self):
        """
        Reset the SR150 device to boot the new firmware.
        This implementation toggles the chip enable (CE) pin.
        """
        print("Resetting device...")
        self.ce.value(0)
        time.sleep_ms(100)
        self.ce.value(1)
        time.sleep_ms(100)
        print("Device reset complete.")

    def upload_firmware(self, firmware_path, max_attempts=3):
        """
        Upload firmware to the SR150 from a binary file.
        The method reads the firmware file in chunks and sends each chunk over SPI,
        while comparing the sent data with the received data. It retries up to `max_attempts`
        if an error is detected during the upload.
        """
        print("Starting firmware upload from", firmware_path)
        attempt = 0

        while attempt < max_attempts:
            attempt += 1
            print(f"Attempt {attempt} of {max_attempts}...")
            try:
                with open(firmware_path, 'rb') as fw:
                    while True:
                        chunk = fw.read(256)  # send in 256-byte chunks
                        if not chunk:
                            break

                        # Prepare a buffer to receive data during the SPI transaction
                        received_chunk = bytearray(len(chunk))  # Initialize the buffer to store received data

                        # Perform the simultaneous transmission and reception of data
                        self.cs.value(0)
                        self.spi.write_readinto(chunk, received_chunk)  # Write chunk and read into the buffer
                        self.cs.value(1)

                        # Compare sent and received data
                        if chunk != received_chunk:
                            print("Error: Sent and received data do not match.\r", end="")
                            print(f"Sent: {chunk}")
                            print(f"Received: {received_chunk}")
                            # Reset the device and try again
                            print("Resetting device and retrying...")
                            self.reset_device()
                            break  # Exit the inner loop to restart the upload process
                        else:
                            print("Data sent and received match.")

                    print("Firmware upload complete")
                    return  # If we complete the upload successfully, exit the method
            except Exception as e:
                print(f"Firmware upload failed on attempt {attempt}: {e}")
                # Reset the device and try again
                print("Resetting device and retrying...")
                self.reset_device()

        # After max attempts, print an error message
        print("Firmware upload failed after 3 attempts.")

    def check_device_status(self):
        """
        After firmware upload, check if the SR150 device is ready and responsive.
        This will send a simple UCI command and check the response.
        """
        print("Checking device status...")
        # Example UCI command for device status (replace with actual command)
        device_status_payload = bytearray([0x01])  # Example payload, adjust as per UCI spec
        self.send_command(0x01, device_status_payload)  # Sending device status command

        # Read the response while sending zeros to keep the interface active
        response = self.read_response(256)  # Adjust the length based on the expected response
        print("Device response:", response)

        # Check if the response is non-empty
        if response:
            print("UCI communication successful.")
        else:
            print("Error: No response received from the SR150.")

    def run(self):
        """
        Example method to send a command and print the response.
        Replace this with the actual logic needed for your application.
        """
        print("Sending a test command...")
        self.send_command(0x01, b'\x00\x01')
        response = self.read_response(64)
        print("Received response:", response)

# Create an instance of the SR150 device driver
#sr150 = SR150(spi, cs, ce, irq)

# On startup, upload firmware from a binary file (ensure firmware.bin exists on your filesystem)
#sr150.upload_firmware("firmware.bin")

# Check if UCI communication is now working after firmware upload
#sr150.check_device_status()

# Optionally, run a test command after firmware update:
#sr150.run()

