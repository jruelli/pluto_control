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

    def get_state(self):
        command = f"em_btn get"
        return self.send_command(command)

    def set_enabled(self, value):
        command = f"em_btn set {value}"
        self.send_command(command)

    def initialize(self):
        self.set_enabled(self.config['enabled'])
        return self.get_state()


class EmBtnController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.initialize()

    def initialize(self):
        em_btn_config = self.load_em_btn_config()
        embtn = EmBtn(em_btn_config, self.send_command, self.receive_command)
        embtn.initialize()

    def load_em_btn_config(self):
        section = f'EM_BTN_CONFIG'
        return {
            'enabled': self.config.getint(section, 'enabled', fallback=0)
        }
