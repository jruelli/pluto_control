# -*- coding: utf-8 -*-
"""
This module contains
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class PlutoPico:
    def __init__(self, config_file, existing_serial_handler):
        self.config = config_file
        self.serial_handler = existing_serial_handler
        self.motors = []
        self.hand_brake = True
        self.current_state = 'stopped'
        self.relay_state = 0
        self.keyboard_enabled = False
        self.key_mappings = self.load_key_mappings()
        self.initialize_motors()

    def initialize_motors(self):
        for motor_number in range(1, 3):
            motor_config = self.load_motor_config(motor_number)
            motor = self.Motor(motor_number, motor_config, self.send_command, self.receive_command)
            self.motors.append(motor)

    def load_motor_config(self, motor_number):
        section = f'MOTOR_{motor_number}_CONFIG'
        return {
            'direction': self.config.getint(section, 'direction', fallback=0),
            'max_speed': self.config.getint(section, 'max_speed', fallback=0),
            'accel_rate': self.config.getint(section, 'accel_step_size', fallback=100),
            'brake_rate': self.config.getint(section, 'brake_step_size', fallback=100),
            'accel_delay': self.config.getint(section, 'accel_step_delay', fallback=1),
            'brake_delay': self.config.getint(section, 'brake_step_delay', fallback=1),
        }

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

    def send_command(self, command):
        command_with_newline = command + "\n"
        self.serial_handler.write(command_with_newline.encode('utf-8'))
        self.receive_command()

    def receive_command(self):
        response = self.serial_handler.read()
        return response

    def set_motors(self, speed_motor1, dir_motor1, speed_motor2, dir_motor2):
        command = f"motors set {speed_motor1} {dir_motor1} {speed_motor2} {dir_motor2}"
        self.send_command(command)

    class Motor:
        def __init__(self, motor_number, config, send_command_func, receive_command_func):
            self.motor_number = motor_number
            self.config = config
            self.send_command = send_command_func
            self.receive_command = receive_command_func

        def set_direction(self, state):
            command = f"motor{self.motor_number} set-dir {state}"
            self.send_command(command)

        def set_accel_rate(self, value):
            command = f"motor{self.motor_number} config-acc-rate {value}"
            self.send_command(command)

        def set_brake_rate(self, value):
            command = f"motor{self.motor_number} config-brak-rate {value}"
            self.send_command(command)

        def set_accel_delay(self, value):
            command = f"motor{self.motor_number} config-acc-rate-delay {value}"
            self.send_command(command)

        def set_brake_delay(self, value):
            command = f"motor{self.motor_number} config-brak-rate-delay {value}"
            self.send_command(command)

        def initialize(self):
            self.set_direction(self.config['direction'])
            self.set_accel_rate(self.config['accel_rate'])
            self.set_brake_rate(self.config['brake_rate'])
            self.set_accel_delay(self.config['accel_delay'])
            self.set_brake_delay(self.config['brake_delay'])

    def initialize(self):
        for motor in self.motors:
            motor.initialize()

    def enable_keyboard_control(self):
        self.keyboard_enabled = True

    def disable_keyboard_control(self):
        self.keyboard_enabled = False
        self.hand_brake = False
        # Engage handbrake
        self.set_handbrake()

    def set_handbrake(self):
        self.hand_brake = not self.hand_brake
        pi.logger.debug(f"handbrake set to: {self.hand_brake}")
        if self.hand_brake:
            pi.logger.debug("Motor turned off!")
            self.stop()

    def go_forward(self):
        if self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.stop()
        elif self.current_state in ['back', 'back-left', 'back-right']:
            pi.logger.debug("stopping backward movement")
            self.stop()
        elif self.current_state != 'forward':
            pi.logger.debug("going forward")
            self.set_motors(self.motors[0].config['max_speed'], self.motors[0].config['direction'],
                            self.motors[1].config['max_speed'], self.motors[1].config['direction'])
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
            self.set_motors(self.motors[0].config['max_speed'], 1 - self.motors[0].config['direction'],
                            self.motors[1].config['max_speed'], 1 - self.motors[1].config['direction'])
            self.current_state = 'back'

    def stop(self):
        pi.logger.debug("stopping")
        self.set_motors(0, 0, 0, 0)
        self.current_state = 'stopped'

    def turn_left(self):
        if not self.hand_brake:
            if self.current_state == 'forward':
                pi.logger.debug("turning forward-left")
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), self.motors[0].config['direction'],
                                self.motors[1].config['max_speed'], self.motors[1].config['direction'])
                self.current_state = 'forward-left'
            elif self.current_state == 'back':
                pi.logger.debug("turning back-left")
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), 1 - self.motors[0].config['direction'],
                                self.motors[1].config['max_speed'], 1 - self.motors[1].config['direction'])
                self.current_state = 'back-left'
            elif self.current_state == 'back-left' or self.current_state == 'forward-left':
                pi.logger.debug("maintaining left movement")
            elif self.current_state == 'back-right':
                # Go straight back
                self.go_back()
            elif self.current_state == 'forward-right':
                # Go straight forward
                self.go_forward()
            else:
                pi.logger.debug("rotate in place left")
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), 1 - self.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-left'

    def turn_right(self):
        if not self.hand_brake:
            if self.current_state == 'forward':
                pi.logger.debug("turning forward-right")
                self.set_motors(self.motors[0].config['max_speed'], self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), self.motors[1].config['direction'])
                self.current_state = 'forward-right'
            elif self.current_state == 'back':
                pi.logger.debug("turning back-right")
                self.set_motors(self.motors[0].config['max_speed'], 1 - self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), 1 - self.motors[1].config['direction'])
                self.current_state = 'back-right'
            elif self.current_state == 'back-right' or self.current_state == 'forward-right':
                pi.logger.debug("maintaining right movement")
            elif self.current_state == 'forward-right':
                # Go straight forward
                self.go_forward()
            elif self.current_state == 'back-right':
                # Go straight back
                self.go_back()
            else:
                pi.logger.debug("rotate in place right")
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), 1 - self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), self.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-right'

    def rotate_in_place(self, direction):
        if not self.hand_brake:
            if direction == 'left':
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), 1 - self.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-left'
            elif direction == 'right':
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), 1 - self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), self.motors[1].config['direction'])
                self.current_state = 'rotate-in-place-right'

    def toggle_relay(self, relay_number):
        pi.logger.debug(f"Toggling relay: {relay_number}")
        self.relay_state ^= (1 << relay_number)
        command = f"relays --set-bytes {self.relay_state}"
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
