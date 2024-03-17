# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import os
import sys

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

def create_window():
    """
    Creates the Qt Application Window and starts the event loop.
    """
    pi.logger.debug("Creating Qt Application Window")
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
