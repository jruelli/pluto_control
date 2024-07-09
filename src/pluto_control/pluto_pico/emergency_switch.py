# -*- coding: utf-8 -*-
"""
Emergency switch module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class EmBtn:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func

    def get_state(self, log_enabled=True):
        command = f"em_btn get"
        return self.send_command(command, log_enabled)

    def config_mode(self, value):
        command = f"em_btn config-mode {value}"
        self.send_command(command)

    def initialize(self):
        # Retrieve the safety enabled value from the configuration
        safety_enabled = self.config.get('EM_BTN_CONFIG', 'safety_enabled', fallback='1')
        self.config_mode(safety_enabled)

    def load_key_mappings(self):
        # Load the safety_enabled configuration for EmBtn
        mappings = {
            'safety_enabled': self.config.get('EM_BTN_CONFIG', 'safety_enabled', fallback='1'),
        }
        return mappings
