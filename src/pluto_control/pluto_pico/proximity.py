# -*- coding: utf-8 -*-
"""
Proximity sensor module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


class Proximity:
    def __init__(self, sensor_number, config, send_command_func, receive_command_func):
        self.sensor_number = sensor_number
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func

    def set_mode(self, mode):
        command = f"proxy config-mode p_{self.sensor_number} {mode[0].lower()}"
        self.send_command(command)

    def set_threshold(self, threshold):
        command = f"proxy set-threshold p_{self.sensor_number} {threshold}"
        self.send_command(command)

    def get_distance(self, log_enabled=True):
        command = f"proxy get-dis p_{self.sensor_number}"
        return self.send_command(command, log_enabled)

    def get_proximity(self):
        command = f"proxy get-prox-state p_{self.sensor_number}"
        return self.send_command(command)

    def initialize(self):
        self.set_mode(self.config['mode'])
        self.set_threshold(self.config['threshold'])


class ProximityController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.proximity = []
        self.initialize_proximity()

    def initialize_proximity(self):
        for sensor_number in range(4):
            sensor_config = self.load_proximity_config(sensor_number)
            proximity = Proximity(sensor_number, sensor_config, self.send_command, self.receive_command)
            self.proximity.append(proximity)

    def load_proximity_config(self, sensor_number):
        section = f'PROXIMITY_SENSOR_{sensor_number}'
        return {
            'mode': self.config.get(section, 'mode', fallback='OFF'),
            'threshold': self.config.getint(section, 'threshold', fallback=100)
        }

    def initialize(self):
        for proximity in self.proximity:
            proximity.initialize()

    def get_distance_sensor(self, log_enabled=True):
        """Update the distance sensor readings."""
        distances = []
        for proximity in self.proximity:
            distance = proximity.get_distance(log_enabled)
            distances.append(distance)
        return distances
