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
        self.populate_devices()

    def populate_devices(self):
        """Populate the combo box with available USB devices."""
        self.cB_PortNumber.addItem("USB Ports")  # Add hint as the first item
        self.cB_PortNumber.model().item(0).setEnabled(False)  # Disable the 'USB Ports' item
        devices = device_manager.list_usb_devices()
        for device in devices:
            pi.logger.debug("Found USB device: " + f"{device.device}")
            self.cB_PortNumber.addItem(f"{device.device} - {device.description}")
        if len(devices) == 0:
            self.cB_PortNumber.addItem("No devices found")
            self.cB_PortNumber.model().item(1).setEnabled(False)  # Disable if no devices found
        else:
            self.cB_PortNumber.setCurrentIndex(1)  # Automatically select the first actual device
            self.pB_Connect.setEnabled(True)

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
        self.populate_devices()
        self.pB_Connect.setEnabled(True)
        self.pB_Disconnect.setEnabled(False)
        self.tE_pluto_pico_version.setText("")

    def connect_and_fetch_version(self):
        """Connect to the selected device and fetch its version."""
        selected_device = self.cB_PortNumber.currentText().split(" - ")[0]
        if selected_device != "USB Ports":
            try:
                self.serial_connection = serial.Serial(selected_device, 115200, timeout=1)
                self.pB_Connect.setEnabled(False)
                self.pB_Disconnect.setEnabled(True)
                time.sleep(2)  # Wait for the device to initialize
                # Turn off echo and prompt (if needed)
                self.serial_connection.write(b"shell echo off\n")
                self.serial_connection.flush()
                time.sleep(0.5)  # Short delay to let the command process
                # Clear any initial data from the buffer
                self.serial_connection.reset_input_buffer()
                # Send the 'version' command
                self.serial_connection.write(b"version\n")
                # Read the response
                time.sleep(0.5)  # Allow time for the device to respond
                response = self.read_response()
                print(response)
                # Read the response
                time.sleep(0.5)  # Allow time for the device to respond
                response = self.read_response()
                print(response)
                # Update the GUI with the version info
                self.tE_pluto_pico_version.setText(response)

            except serial.SerialException as e:
                self.pB_connect.setEnabled(False)
                self.pB_disconnect.setEnabled(False)
                pi.logger.error(f"Serial connection error: {e}")
                self.textEdit_version.setText(f"Failed to connect: {e}")
        else:
            self.textEdit_version.setText("Select a valid USB port.")

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
