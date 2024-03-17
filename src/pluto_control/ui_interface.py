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

from . import pluto_control_ui
from . import proginit as pi
from . import device_manager

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
        self.setupUi(self)
        pi.logger.debug("Setup UI")
        self.pB_connect.clicked.connect(self.connect_and_fetch_version)
        self.populate_devices()


    def populate_devices(self):
        """Populate the combo box with available USB devices."""
        self.comboBox_ports.addItem("USB Ports")  # Add hint as the first item
        self.comboBox_ports.model().item(0).setEnabled(False)  # Disable the 'USB Ports' item
        devices = device_manager.list_usb_devices()
        for device in devices:
            pi.logger.debug("Found USB device: " + f"{device.device}")
            self.comboBox_ports.addItem(f"{device.device} - {device.description}")
        if len(devices) == 0:
            self.comboBox_ports.addItem("No devices found")
            self.comboBox_ports.model().item(1).setEnabled(False)  # Disable if no devices found
        else:
            self.comboBox_ports.setCurrentIndex(1)  # Automatically select the first actual device
            self.pB_connect.setEnabled(True)

    def connect_and_fetch_version(self):
        """Connect to the selected device and fetch its version."""
        selected_device = self.comboBox_ports.currentText().split(" - ")[0]
        if selected_device != "USB Ports":
            try:
                self.serial_connection = serial.Serial(selected_device, 115200, timeout=1)
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
                version_number = self.extract_version_number(response)

                # Update the GUI with the version info
                self.textEdit_version.setText(version_number)

            except serial.SerialException as e:
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

    def extract_version_number(self, version_string):
        # This function assumes the version string format "App Version: x.y.z-unstable"
        # Adjust the slicing as needed if the format changes
        match = re.search(r'\d+\.\d+\.\d+', version_string)
        return match.group(0) if match else "Unknown version"

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
