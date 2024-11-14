# -*- coding: utf-8 -*-
"""
Proximity sensor module for pluto_pico
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import proginit as pi


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
        mode_char = mode[0].lower()  # Translate to 'o', 'd', or 'p'
        command = f"proxy config-mode p_{self.sensor_number} {mode_char}"
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
        self.set_mode(self.config["mode"])
        self.set_threshold(self.config["threshold"])


class ProximityController:
    def __init__(self, config, send_command_func, receive_command_func):
        self.config = config
        self.send_command = send_command_func
        self.receive_command = receive_command_func
        self.proximity_sensors = []
        self.initialize_proximity_sensors()

    def initialize_proximity_sensors(self):
        for sensor_number in range(4):
            sensor_config = self.load_proximity_config(sensor_number)
            proximity_sensor = Proximity(sensor_number, sensor_config, self.send_command, self.receive_command)
            self.proximity_sensors.append(proximity_sensor)

    def load_proximity_config(self, sensor_number):
        section = f"PROXIMITY_CONFIG"
        mode = self.config.get(section, f"p{sensor_number}_mode", fallback="o")
        threshold = self.config.getint(section, f"p{sensor_number}_threshold", fallback=100)
        return {"mode": mode, "threshold": threshold}

    def initialize(self):
        for proximity_sensor in self.proximity_sensors:
            proximity_sensor.initialize()

    def get_distance_sensor(self, log_enabled=True):
        """Update the distance sensor readings."""
        distances = []
        for proximity_sensor in self.proximity_sensors:
            distance = proximity_sensor.get_distance(log_enabled)
            distances.append(distance)
        return distances
