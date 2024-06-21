# -*- coding: utf-8 -*-
"""
Emergency switch module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class Temperature:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func

    def get_temperature_t0(self):
        command = f"temperature t_0 get"
        return self.send_command(command)

    def get_temperature_t1(self):
        command = f"temperature t_1 get"
        return self.send_command(command)

    def get_temperature_t2(self):
        command = f"temperature t_2 get"
        return self.send_command(command)

    def initialize(self):
        self.get_temperature_t0()
        self.get_temperature_t1()
        self.get_temperature_t2()


class TemperatureController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.initialize()

    def initialize(self):
        temperature_config = self.load_temperature_config()
        embtn = Temperature(temperature_config, self.send_command, self.receive_command)
        embtn.initialize()

    def load_temperature_config(self):
        section = f'TEMP_CONFIG'
        # TODO: add useful configuration or delete this function
        return {
            'enabled': self.config.getint(section, 'enabled', fallback=0)
        }
