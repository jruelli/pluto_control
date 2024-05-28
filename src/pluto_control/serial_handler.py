import serial
import serial.tools.list_ports
import re
import proginit as pi


class SerialHandler:
    def __init__(self, log_callback):
        """
        Initialize the SerialHandler.

        Args:
            log_callback (function): Callback function for logging messages.
        """
        self.serial_connection = None
        self.log_callback = log_callback

    def connect(self, port, baudrate=115200, timeout=1):
        """
        Connect to a serial port.

        Args:
            port (str): The port to connect to.
            baudrate (int): The baudrate for the connection.
            timeout (int): The timeout for the connection.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            self.serial_connection = serial.Serial(port, baudrate, timeout=timeout)
            pi.logger.debug(f"Connected to {port}")
            return True
        except serial.SerialException as e:
            pi.logger.error(f"Serial connection error: {e}")
            return False

    def disconnect(self):
        """Disconnect the serial connection."""
        if self.serial_connection and self.serial_connection.is_open:
            try:
                self.serial_connection.flushOutput()
                self.serial_connection.flushInput()
                self.serial_connection.close()
                pi.logger.debug("Disconnected from device.")
            except (serial.SerialException, ValueError) as e:
                pi.logger.error(f"Error closing serial connection: {e}")
            finally:
                self.serial_connection = None

    def write(self, message):
        """
        Write a message to the serial connection.

        Args:
            message (bytes): The message to send.
        """
        if self.serial_connection:
            self.serial_connection.write(message)
            self.log_callback(message.decode('utf-8').strip(), "send")

    def read(self):
        """
        Read a response from the serial connection.

        Returns:
            str: The response from the device.
        """
        response = ""
        if self.serial_connection:
            try:
                response = self.serial_connection.read_until(b'\n').decode('utf-8', 'ignore').strip()
                response = self.remove_ansi_escape_sequences(response)
                self.log_callback(response, "receive")
            except serial.SerialTimeoutException as e:
                self.log_callback(f"Timeout while reading from serial: {e}", "receive")
        return response

    def flush_echoed_command(self):
        """Flush the echoed command from the serial buffer."""
        try:
            while True:
                line = self.serial_connection.readline()
                if not line:
                    break
                # Optionally, log the discarded echoed command
                pi.logger.debug(f"Discarded echoed command: {line.decode('utf-8').strip()}")
        except serial.SerialTimeoutException as e:
            pi.logger.error(f"Timeout while flushing echoed command: {e}")

    @staticmethod
    def remove_ansi_escape_sequences(text):
        """
        Remove ANSI escape sequences from text.

        Args:
            text (str): The text to clean.

        Returns:
            str: The cleaned text.
        """
        ansi_escape_pattern = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape_pattern.sub('', text)
