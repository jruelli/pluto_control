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
        self.load_proximity_config()
        self.load_temperature_config()
        self.load_battery_config()
        self.load_embtn_config()

        # Connect the save button
        self.buttonBox.accepted.connect(self.save_key_config)

    def load_control_keys(self):
        """Load the control keys from configuration and set them in the UI."""
        pi.logger.debug("Loading Default Control Keys ControlConfigWindow")
        forward_key = pi.conf.get("CONTROL_CONFIG", "forward", fallback="w")
        back_key = pi.conf.get("CONTROL_CONFIG", "back", fallback="s")
        left_key = pi.conf.get("CONTROL_CONFIG", "left", fallback="a")
        right_key = pi.conf.get("CONTROL_CONFIG", "right", fallback="d")
        stop_key = pi.conf.get("CONTROL_CONFIG", "handbrake", fallback="m")

        self.kSE_forward.setKeySequence(forward_key)
        self.kSE_back.setKeySequence(back_key)
        self.kSE_left.setKeySequence(left_key)
        self.kSE_right.setKeySequence(right_key)
        self.kSE_stop.setKeySequence(stop_key)

    def load_relay_keys(self):
        """Load the relay keys from configuration and set them in the UI."""
        pi.logger.debug("Loading Default Relay Keys ControlConfigWindow")
        for i in range(8):
            relay_key = pi.conf.get("CONTROL_CONFIG", f"r{i}", fallback=str(i))
            getattr(self, f"kSE_r{i}").setKeySequence(relay_key)

    def load_motor_config(self, motor_number):
        """Load the motor configuration from the configuration file and set it in the UI."""
        pi.logger.debug(f"Loading Em_Btn {motor_number} Configuration")
        section = f"MOTOR_{motor_number}_CONFIG"
        # Get config values
        max_speed = pi.conf.getint(section, "max_speed", fallback=1)
        accel_step_size = pi.conf.getint(section, "accel_step_size", fallback=5)
        accel_step_delay = pi.conf.getint(section, "accel_step_delay", fallback=100)
        brake_step_size = pi.conf.getint(section, "brake_step_size", fallback=99)
        brake_step_delay = pi.conf.getint(section, "brake_step_delay", fallback=100)
        direction = pi.conf.getint(section, "direction", fallback=0)
        # Set values of elements
        getattr(self, f"sB_max_speed_{motor_number}").setValue(max_speed)
        getattr(self, f"sB_Accel_step_{motor_number}").setValue(accel_step_size)
        getattr(self, f"sB_Accel_delay_{motor_number}").setValue(accel_step_delay)
        getattr(self, f"sB_Brake_step_{motor_number}").setValue(brake_step_size)
        getattr(self, f"sB_Brake_delay_{motor_number}").setValue(brake_step_delay)
        getattr(self, f"cB_dir_{motor_number}").setCurrentIndex(direction)

    def load_proximity_config(self):
        """Load the proximity configuration from the configuration file and set it in the UI."""
        pi.logger.debug("Loading Proximity Configuration")
        for i in range(4):
            mode = pi.conf.get("PROXIMITY_CONFIG", f"p{i}_mode", fallback="o")
            threshold = pi.conf.getint("PROXIMITY_CONFIG", f"p{i}_threshold", fallback=50)
            # Translate 'o' to 0 (index for "OFF"), 'd' to 1 (index for "Distance"), and 'p' to 2 (index for "Proximity")
            if mode == "o":
                getattr(self, f"cB_mode_p{i}").setCurrentIndex(0)
            elif mode == "d":
                getattr(self, f"cB_mode_p{i}").setCurrentIndex(1)
            else:
                getattr(self, f"cB_mode_p{i}").setCurrentIndex(2)
            getattr(self, f"tE_threshhold_p{i}").setText(str(threshold))

    def load_temperature_config(self):
        """Load the temperature configuration from the configuration file and set it in the UI."""
        pi.logger.debug("Loading Temperature Configuration")
        for i in range(3):
            safety_enabled = pi.conf.get("TEMP_CONFIG", f"t{i}_safety_enabled", fallback="d")
            threshold_temp = pi.conf.getfloat("TEMP_CONFIG", f"t{i}_threshold_temp", fallback=60 + i)
            # Translate 'e' to 0 (index for "Enabled") and 'd' to 1 (index for "Disabled")
            if safety_enabled == "e":
                getattr(self, f"cB_temp_func_{i}").setCurrentIndex(0)
            else:
                getattr(self, f"cB_temp_func_{i}").setCurrentIndex(1)
            getattr(self, f"tE_temp_threshold_{i}").setText(str(threshold_temp))

    def load_battery_config(self):
        pi.logger.debug("Loading Battery Configuration")
        for i in range(4):
            safety_enabled = pi.conf.get("BATTERY_CONFIG", f"b{i}_safety_enabled", fallback="d")
            threshold_temp = pi.conf.getfloat("BATTERY_CONFIG", f"b{i}_threshold_voltage", fallback=0.69 + 0.01)
            # Translate 'e' to 0 (index for "Enabled") and 'd' to 1 (index for "Disabled")
            if safety_enabled == "e":
                getattr(self, f"cB_bat_func_{i}").setCurrentIndex(0)
            else:
                getattr(self, f"cB_bat_func_{i}").setCurrentIndex(1)
            getattr(self, f"tE_bat_threshold_{i}").setText(str(threshold_temp))

    def load_embtn_config(self):
        pi.logger.debug("Loading EmBtn Configuration")
        safety_enabled = pi.conf.get("EM_BTN_CONFIG", f"safety_enabled", fallback="0")
        # Translate 'e' to 0 (index for "Enabled") and 'd' to 1 (index for "Disabled")
        if safety_enabled == "1":
            getattr(self, f"cB_embtn_func").setCurrentIndex(0)
        else:
            getattr(self, f"cB_embtn_func").setCurrentIndex(1)

    def save_control_keys(self):
        """Save the control keys configuration to the config file."""
        forward_key = self.kSE_forward.keySequence().toString()
        back_key = self.kSE_back.keySequence().toString()
        left_key = self.kSE_left.keySequence().toString()
        right_key = self.kSE_right.keySequence().toString()
        handbrake_key = self.kSE_stop.keySequence().toString()

        pi.conf.set("CONTROL_CONFIG", "forward", forward_key)
        pi.conf.set("CONTROL_CONFIG", "back", back_key)
        pi.conf.set("CONTROL_CONFIG", "left", left_key)
        pi.conf.set("CONTROL_CONFIG", "right", right_key)
        pi.conf.set("CONTROL_CONFIG", "handbrake", handbrake_key)

    def save_relay_keys(self):
        """Save the relay keys configuration to the config file."""
        for i in range(8):
            relay_key = getattr(self, f"kSE_r{i}").keySequence().toString()
            pi.conf.set("CONTROL_CONFIG", f"r{i}", relay_key)

    def save_motor_config(self, motor_number):
        """Save the motor configuration to the config file."""
        section = f"MOTOR_{motor_number}_CONFIG"

        max_speed = getattr(self, f"sB_max_speed_{motor_number}").value()
        accel_step_size = getattr(self, f"sB_Accel_step_{motor_number}").value()
        accel_step_delay = getattr(self, f"sB_Accel_delay_{motor_number}").value()
        brake_step_size = getattr(self, f"sB_Brake_step_{motor_number}").value()
        brake_step_delay = getattr(self, f"sB_Brake_delay_{motor_number}").value()
        direction = getattr(self, f"cB_dir_{motor_number}").currentIndex()

        pi.conf.set(section, "max_speed", str(max_speed))
        pi.conf.set(section, "accel_step_size", str(accel_step_size))
        pi.conf.set(section, "accel_step_delay", str(accel_step_delay))
        pi.conf.set(section, "brake_step_size", str(brake_step_size))
        pi.conf.set(section, "brake_step_delay", str(brake_step_delay))
        pi.conf.set(section, "direction", str(direction))

    def save_proximity_config(self):
        """Save the proximity configuration to the config file."""
        for i in range(4):
            # Translate comboBox index to 'o', 'd', or 'p'
            mode_index = getattr(self, f"cB_mode_p{i}").currentIndex()
            if mode_index == 0:
                mode = "o"
            elif mode_index == 1:
                mode = "d"
            else:
                mode = "p"
            threshold = getattr(self, f"tE_threshhold_p{i}").toPlainText()
            pi.conf.set("PROXIMITY_CONFIG", f"p{i}_mode", mode)
            pi.conf.set("PROXIMITY_CONFIG", f"p{i}_threshold", threshold)

    def save_temperature_config(self):
        """Save the temperature configuration to the config file."""
        for i in range(3):
            # Translate comboBox index to 'e' or 'd'
            if getattr(self, f"cB_temp_func_{i}").currentIndex() == 0:
                safety_enabled = "e"
            else:
                safety_enabled = "d"
            threshold_temp = getattr(self, f"tE_temp_threshold_{i}").toPlainText()
            pi.conf.set("TEMP_CONFIG", f"t{i}_safety_enabled", safety_enabled)
            pi.conf.set("TEMP_CONFIG", f"t{i}_threshold_temp", str(threshold_temp))

    def save_battery_config(self):
        """Save the battery configuration to the config file."""
        for i in range(4):
            # Translate comboBox index to 'e' or 'd'
            if getattr(self, f"cB_bat_func_{i}").currentIndex() == 0:
                safety_enabled = "e"
            else:
                safety_enabled = "d"
            threshold_temp = getattr(self, f"tE_bat_threshold_{i}").toPlainText()
            pi.conf.set("BATTERY_CONFIG", f"b{i}_safety_enabled", safety_enabled)
            pi.conf.set("BATTERY_CONFIG", f"b{i}_threshold_voltage", str(threshold_temp))

    def save_embtn_config(self):
        """Save the embtn configuration to the config file."""
        # Translate comboBox index to 'e' or 'd'
        if getattr(self, f"cB_embtn_func").currentIndex() == 0:
            safety_enabled = "1"
        else:
            safety_enabled = "0"
        pi.conf.set("EM_BTN_CONFIG", f"safety_enabled", safety_enabled)

    def save_key_config(self):
        """Save all keys configuration to the config file."""
        self.save_control_keys()
        self.save_relay_keys()
        self.save_motor_config(1)
        self.save_motor_config(2)
        self.save_proximity_config()
        self.save_temperature_config()
        self.save_battery_config()
        self.save_embtn_config()
        pi.save_conf()
        pi.logger.debug("Control configuration saved")
