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
import re

from PyQt5 import QtCore, QtWidgets

from . import __about__
from . import pluto_control_ui
from . import control_config
from . import proginit as pi
from . import usb_device_manager
from . import serial_handler
from . import pluto_pico


def extract_version_number(version_string):
    # This function assumes the version string format "App Version: x.y.z-unstable"
    # Adjust the slicing as needed if the format changes
    match = re.search(r"\d+\.\d+\.\d+", version_string)
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
        self.serial_handler = serial_handler.SerialHandler(self.log_pico_communication)
        # Initialize PlutoPico
        self.pluto_pico = pluto_pico.PlutoPico(pi.conf, self.serial_handler)
        self.control_config_window = control_config.ControlConfigWindow()  # Initialize the additional window
        pi.logger.debug("Setup UI")
        self.tE_pluto_control_version.setText("pluto-control version: " + __about__.__version__)
        self.pB_Connect.clicked.connect(self.connect_and_fetch_version)
        self.pB_Disconnect.clicked.connect(self.disconnect_serial_connection)
        self.pB_SaveConfig.clicked.connect(self.save_config)
        self.pB_Control_Config.clicked.connect(self.open_config_window)  # Connect button to open config window
        self.populate_devices()
        self.connected_to_pluto_pico = False

    def populate_devices(self):
        """Populate the combo box with available USB devices."""
        self.cB_PortNumber.clear()  # Clear existing items
        self.cB_PortNumber.addItem("USB Ports")  # Add hint as the first item
        self.cB_PortNumber.model().item(0).setEnabled(False)  # Disable the 'USB Ports' item

        devices = usb_device_manager.list_usb_devices()
        saved_port = pi.conf.get("DEFAULT", "pluto_pico_port", fallback="")

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
        self.serial_handler.disconnect()
        self.pB_Connect.setEnabled(True)
        self.pB_Disconnect.setEnabled(False)
        self.tE_pluto_pico_version.setText("Disconnected")
        self.connected_to_pluto_pico = False
        self.enable_ui_elements_of_pico()

    def connect_and_fetch_version(self):
        """Connect to the selected device and fetch its version."""
        selected_device = self.cB_PortNumber.currentText().split(" - ")[0]
        if selected_device != "USB Ports":
            if self.serial_handler.connect(selected_device):
                self.pB_Connect.setEnabled(False)
                self.pB_Disconnect.setEnabled(True)
                time.sleep(1)
                self.serial_handler.write(b"shell echo off\n")
                self.serial_handler.write(b"shell prompt off\n")
                self.serial_handler.flush_echoed_command()
                self.serial_handler.write(b"version\n")
                response = self.serial_handler.read()
                self.tE_pluto_pico_version.setText(response)
                self.connected_to_pluto_pico = True
                self.enable_ui_elements_of_pico()
                self.pluto_pico = pluto_pico.PlutoPico(pi.conf, self.serial_handler)
                self.pluto_pico.initialize()
            else:
                self.pB_Connect.setEnabled(True)
                self.pB_Disconnect.setEnabled(False)
                self.tE_pluto_pico_version.setText("Failed to connect.")
        else:
            self.tE_pluto_pico_version.setText("Select a valid USB port.")

    def open_config_window(self):
        """Open the additional configuration window."""
        self.control_config_window.show()

    def enable_ui_elements_of_pico(self):
        pi.logger.debug("Enabling other UI elements")
        if self.connected_to_pluto_pico:
            self.pB_Control_Config.setEnabled(True)
        else:
            self.pB_Control_Config.setEnabled(False)

    def save_config(self):
        pi.logger.debug("Saving Configuration")
        pi.conf.set("DEFAULT", "pluto_pico_port", self.cB_PortNumber.currentText().split(" - ")[0])
        pi.save_conf()

    def log_pico_communication(self, message, direction):
        """Add a message to the terminal text edit and log it with direction."""
        prefix = "Sent: " if direction == "send" else "Received: "
        full_message = f"{prefix}{message}"
        self.tE_terminal.append(full_message)
        pi.logger.debug(full_message)


def create_window():
    """
    Creates the Qt Application Window and starts the event loop.
    """
    pi.logger.debug("Creating Qt Application Window")
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
