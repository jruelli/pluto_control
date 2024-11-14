# -*- coding: utf-8 -*-
"""
Relay control module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class RelayController:
    def __init__(self, send_command_func):
        self.send_command = send_command_func
        self.relay_state = 0

    def toggle_relay(self, relay_number):
        pi.logger.debug(f"Toggling relay: {relay_number}")
        self.relay_state ^= 1 << relay_number
        command = f"relays set-relays {self.relay_state}"
        self.send_command(command)

    def relay_0(self):
        self.toggle_relay(0)

    def relay_1(self):
        self.toggle_relay(1)

    def relay_2(self):
        self.toggle_relay(2)

    def relay_3(self):
        self.toggle_relay(3)

    def relay_4(self):
        self.toggle_relay(4)

    def relay_5(self):
        self.toggle_relay(5)

    def relay_6(self):
        self.toggle_relay(6)

    def relay_7(self):
        self.toggle_relay(7)
