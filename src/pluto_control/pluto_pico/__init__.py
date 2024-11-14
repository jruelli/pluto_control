# -*- coding: utf-8 -*-
"""
This module contains the main PlutoPico class.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi

from .motors import MotorController
from .proximity import ProximityController
from .relays import RelayController
from .emergency_switch import EmBtn
from .temperature import Temperature
from .batteries import Batteries
from .control import Control


class PlutoPico:
    def __init__(self, config_file, existing_serial_handler):
        self.config = config_file
        self.serial_handler = existing_serial_handler
        self.control = Control(self.config, self.send_command, self.receive_command)
        self.proximity = ProximityController(self.config, self.send_command, self.receive_command)
        self.relays = RelayController(self.send_command)
        self.em_btn = EmBtn(self.config, self.send_command, self.receive_command)
        self.temperature = Temperature(self.config, self.send_command, self.receive_command)
        self.batteries = Batteries(self.config, self.send_command, self.receive_command)

    def send_command(self, command, log_enabled=True):
        command_with_newline = command + "\n"
        self.serial_handler.write_pluto_pico(command_with_newline.encode('utf-8'), log_enabled)
        response = self.receive_command(log_enabled)
        return response

    def receive_command(self, log_enabled=True):
        response = self.serial_handler.read_pluto_pico(log_enabled)
        return response

    def initialize(self):
        self.proximity.initialize()
        self.em_btn.initialize()
        self.temperature.initialize()
        self.batteries.initialize()

    def set_config_file(self, config):
        self.config = config
