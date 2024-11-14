# -*- coding: utf-8 -*-
"""
Em_Btn module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class Motor:
    def __init__(self, motor_number, config, send_command_func, receive_command_func):
        self.motor_number = motor_number
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func

    def set_direction(self, state):
        command = f"motor{self.motor_number} set-dir {state}"
        self.send_command(command)

    def get_speed(self):
        command = f"motor{self.motor_number} get-speed"
        return self.send_command(command)

    def get_speed_with_direction(self, log_enabled=True):
        command_speed = f"motor{self.motor_number} get-speed"
        command_direction = f"motor{self.motor_number} get-dir"
        speed = self.send_command(command_speed, log_enabled)
        direction = self.send_command(command_direction, log_enabled)
        forward_dir = str(self.config["direction"])
        # set a minus if going backwards, set + if going forward
        if direction != forward_dir:
            speed = "-" + speed
        return speed

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
        self.set_direction(self.config["direction"])
        self.set_accel_rate(self.config["accel_rate"])
        self.set_brake_rate(self.config["brake_rate"])
        self.set_accel_delay(self.config["accel_delay"])
        self.set_brake_delay(self.config["brake_delay"])


class MotorController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.motors = []
        self.initialize_motors()

    def initialize_motors(self):
        for motor_number in range(1, 3):
            motor_config = self.load_motor_config(motor_number)
            motor = Motor(motor_number, motor_config, self.send_command, self.receive_command)
            self.motors.append(motor)

    def load_motor_config(self, motor_number):
        section = f"MOTOR_{motor_number}_CONFIG"
        return {
            "direction": self.config.getint(section, "direction", fallback=0),
            "max_speed": self.config.getint(section, "max_speed", fallback=0),
            "accel_rate": self.config.getint(section, "accel_step_size", fallback=100),
            "brake_rate": self.config.getint(section, "brake_step_size", fallback=100),
            "accel_delay": self.config.getint(section, "accel_step_delay", fallback=1),
            "brake_delay": self.config.getint(section, "brake_step_delay", fallback=1),
        }

    def set_motors(self, speed_motor1, dir_motor1, speed_motor2, dir_motor2):
        command = f"motors set {speed_motor1} {dir_motor1} {speed_motor2} {dir_motor2}"
        self.send_command(command)

    def get_motors_speed_with_direction(self, log_enabled=True):
        motor_speeds = []
        for motor in self.motors:
            speed = motor.get_speed_with_direction(log_enabled)
            motor_speeds.append(speed)
        return motor_speeds

    def initialize(self):
        for motor in self.motors:
            motor.initialize()
