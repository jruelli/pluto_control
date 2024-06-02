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
        self.current_state = 'stopped'  # Possible states: 'stopped', 'forward', 'backward'
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
        elif self.current_state == 'backward':
            pi.logger.debug("stopping backward movement")
            self.stop()
        elif self.current_state != 'forward':
            pi.logger.debug("going forward")
            self.set_motors(self.motors[0].config['max_speed'], self.motors[0].config['direction'],
                            self.motors[1].config['max_speed'], self.motors[1].config['direction'])
            self.current_state = 'forward'
        else:
            pi.logger.debug("already moving forward")

    def go_back(self):
        if self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.stop()
        elif self.current_state == 'forward':
            pi.logger.debug("stopping forward movement")
            self.stop()
        elif self.current_state != 'backward':
            pi.logger.debug("going backward")
            self.set_motors(self.motors[0].config['max_speed'], 1 - self.motors[0].config['direction'],
                            self.motors[1].config['max_speed'], 1 - self.motors[1].config['direction'])
            self.current_state = 'backward'
        else:
            pi.logger.debug("already moving backward")

    def stop(self):
        pi.logger.debug("stopping")
        self.set_motors(0, 0, 0, 0)
        self.current_state = 'stopped'

    def turn_left(self):
        if not self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), self.motors[0].config['direction'],
                            self.motors[1].config['max_speed'], self.motors[1].config['direction'])

    def turn_right(self):
        if not self.hand_brake:
            pi.logger.debug(f"movement blocked: handbrake set to: {self.hand_brake}")
            self.set_motors(self.motors[0].config['max_speed'], self.motors[0].config['direction'],
                            int(self.motors[1].config['max_speed'] * 0.5), self.motors[1].config['direction'])

    def rotate_in_place(self, direction):
        if not self.hand_brake:
            if direction == 'left':
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), 1 - self.motors[1].config['direction'])
            elif direction == 'right':
                self.set_motors(int(self.motors[0].config['max_speed'] * 0.5), 1 - self.motors[0].config['direction'],
                                int(self.motors[1].config['max_speed'] * 0.5), self.motors[1].config['direction'])
