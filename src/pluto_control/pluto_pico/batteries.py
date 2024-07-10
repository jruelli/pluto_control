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
        self.R1 = 3300
        self.R2 = 20000
        self.DiodeVoltage1 = 0.67
        self.DiodeVoltage2 = 0.32
        self.b0_cell_voltage = 2.7
        self.b1_cell_voltage = 2.7
        self.b2_cell_voltage = 2.7
        self.b3_cell_voltage = 2.7

    def convert_adc_to_voltage(self, adc_value, diode_voltage):
        """Convert ADC value to actual voltage using the provided formula."""
        if adc_value == -1:
            return -1
        measured_voltage = adc_value
        cell_voltage = (measured_voltage / self.R1) * self.R2 + diode_voltage
        return cell_voltage

    def convert_voltage_to_adc(self, cell_voltage, diode_voltage):
        """Convert cell voltage to ADC value using the provided formula."""
        measured_voltage = ((float(cell_voltage) - diode_voltage) / self.R2) * self.R1
        return measured_voltage

    def get_batteries_b0(self, log_enabled=True):
        command = "ads1115 get-input 0"
        response = self.send_command(command, log_enabled)
        # Remove any unwanted prefix like "0: "
        adc_value_str = response.split(": ")[-1]
        adc_value = float(adc_value_str)
        self.b0_cell_voltage = self.convert_adc_to_voltage(adc_value, self.DiodeVoltage2)
        return self.b0_cell_voltage

    def get_batteries_b1(self, log_enabled=True):
        command = "ads1115 get-input 1"
        response = self.send_command(command, log_enabled)
        # Remove any unwanted prefix like "1: "
        adc_value_str = response.split(": ")[-1]
        adc_value = float(adc_value_str)
        cell_voltage_b1 = self.convert_adc_to_voltage(adc_value, self.DiodeVoltage2)
        if cell_voltage_b1 == -1 or self.b0_cell_voltage == -1:
            self.b1_cell_voltage = -1
        else:
            self.b1_cell_voltage = cell_voltage_b1 - self.b0_cell_voltage
        return self.b1_cell_voltage

    def get_batteries_b2(self, log_enabled=True):
        command = "ads1115 get-input 2"
        response = self.send_command(command, log_enabled)
        # Remove any unwanted prefix like "2: "
        adc_value_str = response.split(": ")[-1]
        adc_value = float(adc_value_str)
        cell_voltage_b2 = self.convert_adc_to_voltage(adc_value, self.DiodeVoltage2)
        if cell_voltage_b2 == -1 or self.b1_cell_voltage == -1:
            self.b2_cell_voltage = -1
        else:
            self.b2_cell_voltage = cell_voltage_b2 - self.b1_cell_voltage
        return self.b2_cell_voltage

    def get_batteries_b3(self, log_enabled=True):
        command = "ads1115 get-input 3"
        response = self.send_command(command, log_enabled)
        # Remove any unwanted prefix like "3: "
        adc_value_str = response.split(": ")[-1]
        adc_value = float(adc_value_str)
        cell_voltage_b3 = self.convert_adc_to_voltage(adc_value, self.DiodeVoltage1)
        if cell_voltage_b3 == -1 or self.b2_cell_voltage == -1:
            self.b3_cell_voltage = -1
        else:
            self.b3_cell_voltage = cell_voltage_b3 - self.b2_cell_voltage
        return self.b3_cell_voltage

    def config_mode(self, index, mode):
        command = f"ads1115 config-input {index} {mode}"
        self.send_command(command)

    def config_threshold(self, index, mode, threshold):
        # Ensure the threshold is limited to 4 digits
        if len(str(threshold)) > 6:
            threshold = str(threshold)[:6]  # Truncate to the first 4 digits

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
        self.config_threshold(0, b0_safety_enabled, self.convert_voltage_to_adc(b0_threshold_voltage, self.DiodeVoltage2))
        self.config_threshold(1, b1_safety_enabled, self.convert_voltage_to_adc(b1_threshold_voltage, self.DiodeVoltage2))
        self.config_threshold(2, b2_safety_enabled, self.convert_voltage_to_adc(b2_threshold_voltage, self.DiodeVoltage2))
        self.config_threshold(3, b3_safety_enabled, self.convert_voltage_to_adc(b3_threshold_voltage, self.DiodeVoltage1))
