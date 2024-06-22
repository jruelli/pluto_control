# -*- coding: utf-8 -*-
"""
This module contains the main PlutoPico class.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi

from .motors import MotorController


class Control:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.key_mappings = self.load_key_mappings()
        self.motors = MotorController(self.config, self.send_command, self.receive_command)
        self.motors.initialize()
        self.hand_brake = True
        self.current_state = 'stopped'
        self.keyboard_control_enabled = False
        self.controller_control_enabled = False

    def load_key_mappings(self):
        mappings = {
            'forward': self.config.get('CONTROL_CONFIG', 'forward', fallback='W').upper(),
            'back': self.config.get('CONTROL_CONFIG', 'back', fallback='S').upper(),
            'left': self.config.get('CONTROL_CONFIG', 'left', fallback='A').upper(),
            'right': self.config.get('CONTROL_CONFIG', 'right', fallback='D').upper(),
            'handbrake': self.config.get('CONTROL_CONFIG', 'handbrake', fallback='M').upper(),
        }
        for i in range(8):
            mappings[f'relay_{i}'] = self.config.get('CONTROL_CONFIG', f'relay_{i}', fallback=str(i)).upper()
        return mappings

    def set_handbrake(self, state):
        self.hand_brake = state
        pi.logger.debug(f"handbrake set to: {self.hand_brake}")
        if state:
            pi.logger.debug("Em_Btn turned off!")
            self.stop()

    def get_handbrake(self):
        return self.hand_brake

    def set_keyboard_control(self, state):
        self.keyboard_control_enabled = state

    def get_keyboard_control(self):
        return self.keyboard_control_enabled

    def set_controller_control(self, state):
        self.controller_control_enabled = state

    def get_controller_control(self):
        return self.controller_control_enabled

    def go_forward(self):
        if self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.stop()
        elif self.current_state in ['back', 'back-left', 'back-right']:
            pi.logger.debug("stopping backward movement")
            self.stop()
        elif self.current_state != 'forward':
            pi.logger.debug("going forward")
            self.motors.set_motors(self.motors.motors[0].config['max_speed'], self.motors.motors[0].config['direction'],
                                   self.motors.motors[1].config['max_speed'], self.motors.motors[1].config['direction'])
            self.current_state = 'forward'

    def go_back(self):
        if self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.stop()
        elif self.current_state in ['forward', 'forward-left', 'forward-right']:
            pi.logger.debug("stopping forward movement")
            self.stop()
        elif self.current_state != 'back':
            pi.logger.debug("going backward")
            self.motors.set_motors(self.motors.motors[0].config['max_speed'], 1 - self.motors.motors[0].config['direction'],
                                   self.motors.motors[1].config['max_speed'], 1 - self.motors.motors[1].config['direction'])
            self.current_state = 'back'

    def stop(self):
        pi.logger.debug("stopping")
        self.motors.set_motors(0, 0, 0, 0)
        self.current_state = 'stopped'

    def turn_left(self):
        if not self.hand_brake:
            if self.current_state == 'forward':
                pi.logger.debug("turning forward-left")
                self.motors.set_motors(int(self.motors.motors[0].config['max_speed'] * 0.5), self.motors.motors[0].config['direction'],
                                       self.motors.motors[1].config['max_speed'], self.motors.motors[1].config['direction'])
                self.current_state = 'forward-left'
            elif self.current_state == 'back':
                pi.logger.debug("turning back-left")
                self.motors.set_motors(int(self.motors.motors[0].config['max_speed'] * 0.5), 1 - self.motors.motors[0].config['direction'],
                                       self.motors.motors[1].config['max_speed'], 1 - self.motors.motors[1].config['direction'])
                self.current_state = 'back-left'
            elif self.current_state == 'back-left' or self.current_state == 'forward-left':
                pi.logger.debug("maintaining left movement")
            elif self.current_state == 'back-right':
                self.go_back()
            elif self.current_state == 'forward-right':
                self.go_forward()
            else:
                pi.logger.debug("rotate in place left")
                self.motors.set_motors(int(self.motors.motors[0].config['max_speed'] * 0.5), self.motors.motors[0].config['direction'],
                                       int(self.motors.motors[1].config['max_speed'] * 0.5), 1 - self.motors.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-left'

    def turn_right(self):
        if not self.hand_brake:
            if self.current_state == 'forward':
                pi.logger.debug("turning forward-right")
                self.motors.set_motors(self.motors.motors[0].config['max_speed'], self.motors.motors[0].config['direction'],
                                       int(self.motors.motors[1].config['max_speed'] * 0.5), self.motors.motors[1].config['direction'])
                self.current_state = 'forward-right'
            elif self.current_state == 'back':
                pi.logger.debug("turning back-right")
                self.motors.set_motors(self.motors.motors[0].config['max_speed'], 1 - self.motors.motors[0].config['direction'],
                                       int(self.motors.motors[1].config['max_speed'] * 0.5), 1 - self.motors.motors[1].config['direction'])
                self.current_state = 'back-right'
            elif self.current_state == 'back-right' or self.current_state == 'forward-right':
                pi.logger.debug("maintaining right movement")
            elif self.current_state == 'forward-right':
                self.go_forward()
            elif self.current_state == 'back-right':
                self.go_back()
            else:
                pi.logger.debug("rotate in place right")
                self.motors.set_motors(int(self.motors.motors[0].config['max_speed'] * 0.5), 1 - self.motors.motors[0].config['direction'],
                                       int(self.motors.motors[1].config['max_speed'] * 0.5), self.motors.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-right'
