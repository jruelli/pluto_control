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

        # Load the current control keys from config
        self.load_control_keys()
        self.load_relay_keys()
        self.load_motor_config(1)
        self.load_motor_config(2)

        # Connect the save button
        self.buttonBox.accepted.connect(self.save_key_config)

    def load_control_keys(self):
        """Load the control keys from configuration and set them in the UI."""
        pi.logger.debug("Loading Default Control Keys ControlConfigWindow")
        forward_key = pi.conf.get('CONTROL_CONFIG', 'forward', fallback='w')
        back_key = pi.conf.get('CONTROL_CONFIG', 'back', fallback='s')
        left_key = pi.conf.get('CONTROL_CONFIG', 'left', fallback='a')
        right_key = pi.conf.get('CONTROL_CONFIG', 'right', fallback='d')
        stop_key = pi.conf.get('CONTROL_CONFIG', 'stop', fallback='space')

        self.kSE_forward.setKeySequence(forward_key)
        self.kSE_back.setKeySequence(back_key)
        self.kSE_left.setKeySequence(left_key)
        self.kSE_right.setKeySequence(right_key)
        self.kSE_stop.setKeySequence(stop_key)

    def load_relay_keys(self):
        """Load the relay keys from configuration and set them in the UI."""
        pi.logger.debug("Loading Default Relay Keys ControlConfigWindow")
        for i in range(8):
            relay_key = pi.conf.get('CONTROL_CONFIG', f'r{i}', fallback=str(i))
            getattr(self, f'kSE_r{i}').setKeySequence(relay_key)

    def load_motor_config(self, motor_number):
        """Load the motor configuration from the configuration file and set it in the UI."""
        pi.logger.debug(f"Loading Motor {motor_number} Configuration")
        section = f'MOTOR_{motor_number}_CONFIG'
        # Get config values
        max_speed = pi.conf.getint(section, 'max_speed', fallback=1)
        accel_step_size = pi.conf.getint(section, 'accel_step_size', fallback=5)
        accel_step_delay = pi.conf.getint(section, 'accel_step_delay', fallback=100)
        brake_step_size = pi.conf.getint(section, 'brake_step_size', fallback=99)
        brake_step_delay = pi.conf.getint(section, 'brake_step_delay', fallback=100)
        direction = pi.conf.getint(section, 'direction', fallback=0)
        # Set values of elements
        getattr(self, f'sB_max_speed_{motor_number}').setValue(max_speed)
        getattr(self, f'sB_Accel_step_{motor_number}').setValue(accel_step_size)
        getattr(self, f'sB_Accel_delay_{motor_number}').setValue(accel_step_delay)
        getattr(self, f'sB_Brake_step_{motor_number}').setValue(brake_step_size)
        getattr(self, f'sB_Brake_delay_{motor_number}').setValue(brake_step_delay)
        getattr(self, f'cB_dir_{motor_number}').setCurrentIndex(direction)

    def save_control_keys(self):
        """Save the control keys configuration to the config file."""
        forward_key = self.kSE_forward.keySequence().toString()
        back_key = self.kSE_back.keySequence().toString()
        left_key = self.kSE_left.keySequence().toString()
        right_key = self.kSE_right.keySequence().toString()
        stop_key = self.kSE_stop.keySequence().toString()

        pi.conf.set('CONTROL_CONFIG', 'forward', forward_key)
        pi.conf.set('CONTROL_CONFIG', 'back', back_key)
        pi.conf.set('CONTROL_CONFIG', 'left', left_key)
        pi.conf.set('CONTROL_CONFIG', 'right', right_key)
        pi.conf.set('CONTROL_CONFIG', 'stop', stop_key)

    def save_relay_keys(self):
        """Save the relay keys configuration to the config file."""
        for i in range(8):
            relay_key = getattr(self, f'kSE_r{i}').keySequence().toString()
            pi.conf.set('CONTROL_CONFIG', f'r{i}', relay_key)

    def save_motor_config(self, motor_number):
        """Save the motor configuration to the config file."""
        section = f'MOTOR_{motor_number}_CONFIG'

        max_speed = getattr(self, f'sB_max_speed_{motor_number}').value()
        accel_step_size = getattr(self, f'sB_Accel_step_{motor_number}').value()
        accel_step_delay = getattr(self, f'sB_Accel_delay_{motor_number}').value()
        brake_step_size = getattr(self, f'sB_Brake_step_{motor_number}').value()
        brake_step_delay = getattr(self, f'sB_Brake_delay_{motor_number}').value()
        direction = getattr(self, f'cB_dir_{motor_number}').currentIndex()

        pi.conf.set(section, 'max_speed', str(max_speed))
        pi.conf.set(section, 'accel_step_size', str(accel_step_size))
        pi.conf.set(section, 'accel_step_delay', str(accel_step_delay))
        pi.conf.set(section, 'brake_step_size', str(brake_step_size))
        pi.conf.set(section, 'brake_step_delay', str(brake_step_delay))
        pi.conf.set(section, 'direction', str(direction))

    def save_key_config(self):
        """Save all keys configuration to the config file."""
        self.save_control_keys()
        self.save_relay_keys()
        self.save_motor_config(1)
        self.save_motor_config(2)
        pi.save_conf()
        pi.logger.debug("Control configuration saved")
