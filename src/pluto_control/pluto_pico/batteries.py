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

    def get_batteries_b0(self):
        command = f"batteries b_0 get"
        return self.send_command(command)

    def get_batteries_b1(self):
        command = f"batteries b_1 get"
        return self.send_command(command)

    def get_batteries_b2(self):
        command = f"batteries b_2 get"
        return self.send_command(command)

    def get_batteries_b3(self):
        command = f"batteries b_3 get"
        return self.send_command(command)

    def initialize(self):
        self.get_batteries_b0()
        self.get_batteries_b1()
        self.get_batteries_b2()
        self.get_batteries_b3()


class BatteriesController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.initialize()

    def initialize(self):
        batteries_config = self.load_batteries_config()
        batteries = Batteries(batteries_config, self.send_command, self.receive_command)
        batteries.initialize()

    def load_batteries_config(self):
        section = f'BATTERY_CONFIG'
        # TODO: add useful configuration or delete this function
        return {
            'enabled': self.config.getint(section, 'enabled', fallback=0)
        }
