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
from .emergency_switch import EmBtnController
from .control import Control


class PlutoPico:
    def __init__(self, config_file, existing_serial_handler):
        self.config = config_file
        self.serial_handler = existing_serial_handler
        self.control = Control(self.config, self.send_command, self.receive_command)
        self.proximity = ProximityController(self.config, self.send_command, self.receive_command)
        self.relays = RelayController(self.send_command)
        self.em_btn = EmBtnController(self.config, self.send_command, self.receive_command)

    def send_command(self, command):
        command_with_newline = command + "\n"
        self.serial_handler.write(command_with_newline.encode('utf-8'))
        response = self.receive_command()
        return response

    def receive_command(self):
        response = self.serial_handler.read()
        return response

    def initialize(self):
        self.proximity.initialize()
        self.em_btn.initialize()
