# control_config.py

# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

from PyQt5 import QtCore, QtWidgets
from . import control_config_ui
import proginit as pi


class ControlConfigWindow(QtWidgets.QDialog, control_config_ui.Ui_Dialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        pi.logger.debug("Setup ControlConfigWindow")
        # Load the current forward key from config
        self.load_forward_key()
        # Connect the save button
        self.buttonBox.accepted.connect(self.save_key_config)

    def load_forward_key(self):
        """Load the forward key from configuration and set it in the UI."""
        pi.logger.debug("Loading Default Keys ControlConfigWindow")
        forward_key = pi.conf.get('CONTROL_CONFIG', 'forward', fallback='w')
        self.kSE_forward.setKeySequence(forward_key)

    def save_key_config(self):
        """Save the forward key configuration to the config file."""
        forward_key = self.kSE_forward.keySequence().toString()
        pi.conf.set('CONTROL_CONFIG', 'forward', forward_key)
        pi.save_conf()
        pi.logger.debug(f"Forward key saved: {forward_key}")
