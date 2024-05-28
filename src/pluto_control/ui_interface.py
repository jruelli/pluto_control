# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import os
import sys
import time
import serial
import serial.tools.list_ports
import re

from PyQt5 import QtCore, QtWidgets

from . import pluto_control_ui, __about__
from . import proginit as pi
from . import device_manager


def extract_version_number(version_string):
    # This function assumes the version string format "App Version: x.y.z-unstable"
    # Adjust the slicing as needed if the format changes
    match = re.search(r'\d+\.\d+\.\d+', version_string)
    return match.group(0) if match else "Unknown version"


class Window(QtWidgets.QMainWindow, pluto_control_ui.Ui_MainWindow):
    """
    Class representing the main window of the pluto_control application.
    """

    def __init__(self, parent=None):
        """
        Constructor for the Window class.

        Args:
             parent (QObject *): The parent widget of the main window. Defaults to None.
        """
        super().__init__(parent)
        self.serial_connection = None
        self.setupUi(self)
        pi.logger.debug("Setup UI")
        self.tE_pluto_control_version.setText("pluto-control version: " + __about__.__version__)
        self.pB_Connect.clicked.connect(self.connect_and_fetch_version)
        self.pB_Disconnect.clicked.connect(self.disconnect_serial_connection)
        self.pB_SaveConfig.clicked.connect(self.save_config)
        self.populate_devices()

    def populate_devices(self):
        """Populate the combo box with available USB devices."""
        self.cB_PortNumber.clear()  # Clear existing items
        self.cB_PortNumber.addItem("USB Ports")  # Add hint as the first item
        self.cB_PortNumber.model().item(0).setEnabled(False)  # Disable the 'USB Ports' item

        devices = device_manager.list_usb_devices()
        saved_port = pi.conf.get('DEFAULT', 'pluto_pico_port', fallback="")  # Get the saved port from the config

        found_saved_port = False
        for device in devices:
            pi.logger.debug("Found USB device: " + f"{device.device}")
            self.cB_PortNumber.addItem(f"{device.device} - {device.description}")
            if device.device == saved_port:
                found_saved_port = True

        if len(devices) == 0:
            self.cB_PortNumber.addItem("No devices found")
            self.cB_PortNumber.model().item(1).setEnabled(False)  # Disable if no devices found
        else:
            if found_saved_port:
                for index in range(1, self.cB_PortNumber.count()):
                    if self.cB_PortNumber.itemText(index).startswith(saved_port):
                        self.cB_PortNumber.setCurrentIndex(index)
                        break
            else:
                pi.logger.error("pluto_pico_port is not available")
                self.cB_PortNumber.setCurrentIndex(1)  # Automatically select the first actual device

        self.pB_Connect.setEnabled(len(devices) > 0)  # Enable connect button only if devices are found

    def disconnect_serial_connection(self):
        if self.serial_connection and self.serial_connection.is_open:
            try:
                # Flush output & input buffer
                self.serial_connection.flushOutput()
                self.serial_connection.flushInput()
                # Close the serial connection
                self.serial_connection.close()
                pi.logger.debug("Serial connection closed")
            except (serial.SerialException, ValueError) as e:
                # Handle exceptions that could be raised by the above operations
                pi.logger.error(f"Error closing serial connection: {e}")
            finally:
                # Ensure that the serial_connection attribute is cleared
                self.serial_connection = None
        # Refresh the list of devices and update the UI accordingly
        self.pB_Connect.setEnabled(True)
        self.pB_Disconnect.setEnabled(False)
        self.tE_pluto_pico_version.setText("Disconnected")

    def connect_and_fetch_version(self):
        """Connect to the selected device and fetch its version."""
        selected_device = self.cB_PortNumber.currentText().split(" - ")[0]
        if selected_device != "USB Ports":
            try:
                self.serial_connection = serial.Serial(selected_device, 115200, timeout=1)
                # Disable the connect button and enable the disconnect button
                self.pB_Connect.setEnabled(False)
                self.pB_Disconnect.setEnabled(True)
                # Wait for the device to initialize
                time.sleep(1)
                # Turn off echo and prompt (if needed)
                self.serial_connection.write(b"shell echo off\n")
                self.serial_connection.write(b"shell prompt off\n")
                # Read and discard echoed command
                self.flush_echoed_command()
                # Clear any initial data from the buffer
                self.serial_connection.reset_input_buffer()
                # Send the 'version' command
                self.serial_connection.write(b"version\n")
                # Read the response
                response = self.read_response()
                # Update the GUI with the version info
                self.tE_pluto_pico_version.setText(response)
            except serial.SerialException as e:
                self.pB_Connect.setEnabled(True)
                self.pB_Disconnect.setEnabled(False)
                pi.logger.error(f"Serial connection error: {e}")
                self.tE_pluto_pico_version.setText(f"Failed to connect: {e}")
        else:
            self.tE_pluto_pico_version.setText("Select a valid USB port.")

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

    def save_config(self):
        pi.logger.debug("Saving Configuration")
        self.pB_SaveConfig.setEnabled(False)
        pi.reload_conf()
        text = pi.conf.get('DEFAULT', 'default_port')
        print(text)

    def read_response(self):
        """Read the response from the device."""
        response = self.serial_connection.read_until(b'\n').decode('utf-8', 'ignore').strip()
        # Remove ANSI escape sequences from response
        response = self.remove_ansi_escape_sequences(response)
        return response.strip()

    @staticmethod
    def remove_ansi_escape_sequences(text):
        # ANSI escape code regex pattern
        ansi_escape_pattern = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape_pattern.sub('', text)


def create_window():
    """
    Creates the Qt Application Window and starts the event loop.
    """
    pi.logger.debug("Creating Qt Application Window")
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
