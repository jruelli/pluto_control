# -*- coding: utf-8 -*-
"""
Emergency switch module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class Batteries:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func

    def get_batteries_b0(self, log_enabled=True):
        command = f"ads1115 get-input 0"
        return self.send_command(command, log_enabled)

    def get_batteries_b1(self, log_enabled=True):
        command = f"ads1115 get-input 1"
        return self.send_command(command, log_enabled)

    def get_batteries_b2(self, log_enabled=True):
        command = f"ads1115 get-input 2"
        return self.send_command(command, log_enabled)

    def get_batteries_b3(self, log_enabled=True):
        command = f"ads1115 get-input 3"
        return self.send_command(command, log_enabled)

    def config_mode(self, index, mode):
        command = f"ads1115 config-input {index} {mode}"
        self.send_command(command)

    def config_threshold(self, index, mode, threshold):
        command = f"ads1115 config-threshold {index} {mode} {threshold}"
        self.send_command(command)

    def initialize(self):
        b0_safety_enabled = self.config.get('BATTERY_CONFIG', 'b0_safety_enabled', fallback='1')
        b1_safety_enabled = self.config.get('BATTERY_CONFIG', 'b1_safety_enabled', fallback='1')
        b2_safety_enabled = self.config.get('BATTERY_CONFIG', 'b2_safety_enabled', fallback='1')
        b3_safety_enabled = self.config.get('BATTERY_CONFIG', 'b3_safety_enabled', fallback='1')
        b0_threshold_voltage = self.config.get('BATTERY_CONFIG', 'b0_threshold_voltage', fallback='0.8')
        b1_threshold_voltage = self.config.get('BATTERY_CONFIG', 'b1_threshold_voltage', fallback='0.8')
        b2_threshold_voltage = self.config.get('BATTERY_CONFIG', 'b2_threshold_voltage', fallback='0.8')
        b3_threshold_voltage = self.config.get('BATTERY_CONFIG', 'b3_threshold_voltage', fallback='0.8')

        self.config_threshold(0, b0_safety_enabled, b0_threshold_voltage)
        self.config_threshold(1, b1_safety_enabled, b1_threshold_voltage)
        self.config_threshold(2, b2_safety_enabled, b2_threshold_voltage)
        self.config_threshold(3, b3_safety_enabled, b3_threshold_voltage)
