# -*- coding: utf-8 -*-
"""
This module contains
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import serial
import serial.tools.list_ports
import re
import proginit as pi


def remove_prompt(response):
    """
    Remove the 'uart:~$' prompt from the response string.

    Args:
        response (str): The response string to process.

    Returns:
        str: The processed response without the prompt.
    """
    prompt = "uart:~$"
    if response.endswith(prompt):
        response = response[: -len(prompt)].strip()
    return response


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

    def write_pluto_pico(self, message, log_enabled=True):
        """
        Write a message to the serial connection.

        Args:
            message (bytes): The message to send.
            log_enabled (bool): If the messages is being logged in terminal
        """
        if self.serial_connection:
            self.serial_connection.write(message)
            if log_enabled:
                self.log_callback(message.decode("utf-8").strip(), "send: ")

    def read_pluto_pico(self, log_enabled=True):
        """
        Read a response from the serial connection.
        Args:
            log_enabled (bool): Whether to log the received message.
        Returns:
            str: The response from the device.
        """
        response = ""
        if self.serial_connection:
            try:
                response = self.serial_connection.read_until(b"$").decode("utf-8", "ignore").strip()
                response = self.remove_ansi_escape_sequences(response)
                response = remove_prompt(response)
                if log_enabled:
                    self.log_callback(response, "receive: ")
            except serial.SerialTimeoutException as e:
                if log_enabled:
                    self.log_callback(f"Timeout while reading from serial: {e}", "receive: ")
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
        ansi_escape_pattern = re.compile(r"(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]")
        return ansi_escape_pattern.sub("", text)
