# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

from PyQt5 import QtCore, QtWidgets
from . import proxy_config_ui
import proginit as pi


class ProxyConfigWindow(QtWidgets.QDialog, proxy_config_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        pi.logger.debug("Setup ProxyConfigWindow")
        self.load_proxy_config()

        # Connect the save button
        self.buttonBox.accepted.connect(self.save_proxy_config)

    def load_proxy_config(self):
        """Load the proxy configuration from the config file and set it in the UI."""
        pi.logger.debug("Loading Proximity Sensor Configuration")
        for sensor_number in range(4):
            section = f"PROXIMITY_SENSOR_{sensor_number}"
            mode = pi.conf.get(section, "mode", fallback="OFF")
            threshold = pi.conf.get(section, "threshold", fallback="100")

            getattr(self, f"cB_mode_p{sensor_number}").setCurrentText(mode)
            getattr(self, f"tE_threshhold_p{sensor_number}").setText(threshold)

    def save_proxy_config(self):
        """Save the proxy configuration to the config file."""
        for sensor_number in range(4):
            section = f"PROXIMITY_SENSOR_{sensor_number}"

            mode = getattr(self, f"cB_mode_p{sensor_number}").currentText()
            threshold = getattr(self, f"tE_threshhold_p{sensor_number}").toPlainText()

            pi.conf.set(section, "mode", mode)
            pi.conf.set(section, "threshold", threshold)

        pi.save_conf()
        pi.logger.debug("Proxy configuration saved")
