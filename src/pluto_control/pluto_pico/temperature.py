# -*- coding: utf-8 -*-
"""
Emergency switch module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"


class Temperature:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.t0_temp = -1
        self.t1_temp = -1
        self.t2_temp = -1
        self.t3_temp = -1
        self.t0_safety_enabled = 0
        self.t1_safety_enabled = 0
        self.t2_safety_enabled = 0
        self.t0_threshold_temp = 0
        self.t1_threshold_temp = 0
        self.t2_threshold_temp = 0

    def get_temperature_t0(self, log_enabled=True):
        command = f"mcp9808 get-sensor 0"
        self.t0_temp = self.send_command(command, log_enabled)
        return self.t0_temp

    def get_temperature_t1(self, log_enabled=True):
        command = f"mcp9808 get-sensor 1"
        self.t1_temp = self.send_command(command, log_enabled)
        return self.t1_temp

    def get_temperature_t2(self, log_enabled=True):
        command = f"mcp9808 get-sensor 2"
        self.t2_temp = self.send_command(command, log_enabled)
        return self.t2_temp

    def is_t0_in_threshold(self, log_enabled=True):
        command = f"mcp9808 get-sensor 0"
        self.t0_temp = self.send_command(command, log_enabled)
        return self.t0_temp

    def config_mode(self, index, mode):
        command = f"mcp9808 config-sensor {index} {mode}"
        self.send_command(command)

    def config_threshold(self, index, mode, threshold):
        command = f"mcp9808 config-threshold {index} {mode} {threshold}"
        self.send_command(command)

    def initialize(self):
        self.t0_safety_enabled = self.config.get('TEMP_CONFIG', 't0_safety_enabled', fallback='e')
        self.t1_safety_enabled = self.config.get('TEMP_CONFIG', 't1_safety_enabled', fallback='e')
        self.t2_safety_enabled = self.config.get('TEMP_CONFIG', 't2_safety_enabled', fallback='e')
        self.t0_threshold_temp = self.config.get('TEMP_CONFIG', 't0_threshold_temp', fallback='69')
        self.t1_threshold_temp = self.config.get('TEMP_CONFIG', 't1_threshold_temp', fallback='69')
        self.t2_threshold_temp = self.config.get('TEMP_CONFIG', 't2_threshold_temp', fallback='69')
        self.config_mode(0, self.t0_safety_enabled)
        self.config_mode(1, self.t1_safety_enabled)
        self.config_mode(2, self.t2_safety_enabled)
        self.config_threshold(0, self.t0_safety_enabled, self.t0_threshold_temp)
        self.config_threshold(1, self.t1_safety_enabled, self.t1_threshold_temp)
        self.config_threshold(2, self.t2_safety_enabled, self.t2_threshold_temp)
