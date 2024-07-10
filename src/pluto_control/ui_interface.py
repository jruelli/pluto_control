# -*- coding: utf-8 -*-
"""
This module contains a PyQt5-based GUI window for a pluto control application.
"""
__author__ = "Jannis Ruellmann"
__copyright__ = "Copyright (C) 2024 Jannis Ruellmann"
__license__ = "MIT"

import os
import sys
import time
import re
import pygame

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QTimer

from . import __about__, proxy_config
from . import pluto_control_ui
from . import control_config
from . import proginit as pi
from . import usb_device_manager
from . import serial_handler
from pluto_pico import PlutoPico
from .pluto_app import PlutoApp  # Import the PlutoApp class


def extract_version_number(version_string):
    match = re.search(r"\d+\.\d+\.\d+", version_string)
    return match.group(0) if match else "Unknown version"


class Window(QtWidgets.QMainWindow, pluto_control_ui.Ui_MainWindow):
    """
    Class representing the main window of the pluto_control application.
    """

    def __init__(self, parent=None):
        """
        Constructor for the Window class.

        Args:
             parent (QObject *): The parent widget of the main window. Defaults to None.
        """
        super().__init__(parent)
        self.serial_connection = None
        self.setupUi(self)
        self.serial_handler = serial_handler.SerialHandler(self.log_pico_communication)
        # Initialize PlutoPico
        self.pluto_pico = PlutoPico(pi.conf, self.serial_handler)
        self.control_config_window = control_config.ControlConfigWindow()
        self.proxy_config_window = proxy_config.ProxyConfigWindow()
        pi.logger.debug("Setup UI")
        self.tE_pluto_control_version.setText("pluto-control version: " + __about__.__version__)
        self.pB_Connect.clicked.connect(self.connect_and_fetch_version)
        self.pB_Disconnect.clicked.connect(self.disconnect_serial_connection)
        self.pB_SaveConfig.clicked.connect(self.save_config)
        self.pB_Control_Config.clicked.connect(self.open_control_config_window)
        self.pB_KeyboardEnable.clicked.connect(self.enable_keyboard_control)
        self.pB_KeyboardDisable.clicked.connect(self.disable_keyboard_control)
        self.pB_ControllerEnable.clicked.connect(self.enable_controller_control)
        self.pB_ControllerDisable.clicked.connect(self.disable_controller_control)
        self.pB_orderConfirmed.clicked.connect(self.order_confirmed_clicked)
        self.pB_orderDelivered.clicked.connect(self.order_delivered_clicked)
        self.pB_orderDispatched.clicked.connect(self.pB_order_dispatched_clicked)
        self.pB_orderCancelled.clicked.connect(self.pB_order_cancelled_clicked)
        self.pB_orderFinished.clicked.connect(self.pB_order_finished_clicked)
        self.populate_devices()
        self.connected_to_pluto_pico = False
        self.timer = QTimer(self)

        # Initialize Pygame for controller support
        pygame.init()
        pygame.joystick.init()
        self.joystick = None
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.poll_controller)

        # Initialize PlutoApp for Firestore integration
        self.pluto_app = PlutoApp("firebase_secret_key.json", self.log_pico_communication)

    def populate_devices(self):
        """Populate the combo box with available USB devices."""
        self.cB_PortNumber.clear()
        self.cB_PortNumber.addItem("USB Ports")
        self.cB_PortNumber.model().item(0).setEnabled(False)

        devices = usb_device_manager.list_usb_devices()
        saved_port = pi.conf.get("DEFAULT", "pluto_pico_port", fallback="")

        found_saved_port = False
        for device in devices:
            pi.logger.debug("Found USB device: " + f"{device.device}")
            self.cB_PortNumber.addItem(f"{device.device} - {device.description}")
            if device.device == saved_port:
                found_saved_port = True

        if len(devices) == 0:
            self.cB_PortNumber.addItem("No devices found")
            self.cB_PortNumber.model().item(1).setEnabled(False)
        else:
            if found_saved_port:
                for index in range(1, self.cB_PortNumber.count()):
                    if self.cB_PortNumber.itemText(index).startswith(saved_port):
                        self.cB_PortNumber.setCurrentIndex(index)
                        break
            else:
                pi.logger.error("pluto_pico_port is not available")
                self.cB_PortNumber.setCurrentIndex(1)

        self.pB_Connect.setEnabled(len(devices) > 0)

    def disconnect_serial_connection(self):
        self.serial_handler.disconnect()
        self.pB_Connect.setEnabled(True)
        self.pB_Disconnect.setEnabled(False)
        self.tE_pluto_pico_version.setText("Disconnected")
        self.connected_to_pluto_pico = False
        self.enable_ui_elements_of_pico()

    def connect_and_fetch_version(self):
        """Connect to the selected device and fetch its version."""
        selected_device = self.cB_PortNumber.currentText().split(" - ")[0]
        if selected_device != "USB Ports":
            if self.serial_handler.connect(selected_device):
                self.pB_Connect.setEnabled(False)
                self.pB_Disconnect.setEnabled(True)
                time.sleep(1)
                self.serial_handler.write_pluto_pico(b"shell echo off\n")
                self.serial_handler.flush_echoed_command()
                self.serial_handler.write_pluto_pico(b"version\n")
                response = self.serial_handler.read_pluto_pico()
                self.tE_pluto_pico_version.setText(response)
                self.connected_to_pluto_pico = True
                self.enable_ui_elements_of_pico()
                self.pluto_pico.initialize()
            else:
                self.pB_Connect.setEnabled(True)
                self.pB_Disconnect.setEnabled(False)
                self.tE_pluto_pico_version.setText("Failed to connect.")
        else:
            self.tE_pluto_pico_version.setText("Select a valid USB port.")

    def open_control_config_window(self):
        """Open the additional configuration window."""
        self.control_config_window.show()

    def enable_ui_elements_of_pico(self):
        pi.logger.debug("Enabling other UI elements")
        if self.connected_to_pluto_pico:
            self.pB_KeyboardEnable.setEnabled(True)
            self.pB_ControllerEnable.setEnabled(True)
            self.timer.timeout.connect(self.update_sensor_values)
            self.timer.start(3000)
        else:
            self.timer.stop()
            self.timer.timeout.disconnect(self.update_sensor_values)

    def save_config(self):
        pi.logger.debug("Saving Configuration")
        pi.conf.set("DEFAULT", "pluto_pico_port", self.cB_PortNumber.currentText().split(" - ")[0])
        pi.save_conf()

    def log_pico_communication(self, message, direction):
        """Add a message to the terminal text edit and log it with direction."""
        full_message = f"{direction}{message}"
        self.tE_terminal.append(full_message)
        pi.logger.debug(full_message)

    def enable_keyboard_control(self):
        self.pluto_pico.control.set_keyboard_control(True)
        self.pB_KeyboardEnable.setChecked(True)
        self.pB_KeyboardDisable.setChecked(False)
        self.pB_KeyboardDisable.setEnabled(True)
        self.pB_KeyboardEnable.setEnabled(False)
        self.installEventFilter(self)
        pi.logger.debug("Keyboard control enabled")

    def disable_keyboard_control(self):
        self.pluto_pico.control.set_keyboard_control(False)
        self.pluto_pico.control.set_handbrake(True)
        self.pB_KeyboardEnable.setChecked(False)
        self.pB_KeyboardDisable.setChecked(True)
        self.pB_KeyboardEnable.setEnabled(True)
        self.pB_KeyboardDisable.setEnabled(False)
        self.removeEventFilter(self)
        pi.logger.debug("Keyboard control disabled")

    def enable_controller_control(self):
        if self.joystick:
            self.pluto_pico.control.set_controller_control(True)
            self.pB_ControllerEnable.setChecked(True)
            self.pB_ControllerDisable.setChecked(False)
            self.pB_ControllerDisable.setEnabled(True)
            self.pB_ControllerEnable.setEnabled(False)
            self.timer.start(100)  # Poll controller every 100 ms
            pi.logger.debug("Controller control enabled")

    def disable_controller_control(self):
        self.pluto_pico.control.set_controller_control(False)
        self.pluto_pico.control.set_handbrake(True)
        self.pB_ControllerEnable.setChecked(False)
        self.pB_ControllerDisable.setChecked(True)
        self.pB_ControllerEnable.setEnabled(True)
        self.pB_ControllerDisable.setEnabled(False)
        self.timer.stop()
        pi.logger.debug("Controller control disabled")

    def order_confirmed_clicked(self):
        pi.logger.debug("Order Confirmed Button clicked")
        # Find the document with "processing" status and update it to "order_confirmed"
        plutito_ref = self.pluto_app.db.collection('plutito')
        query = plutito_ref.where('ordering_state', '==', 'processing').limit(1)
        results = query.stream()
        for doc in results:
            self.pluto_app.update_delivery_status(doc.id, "Confirmed!")
        self.pB_orderConfirmed.setChecked(False)
        self.pB_orderConfirmed.setEnabled(False)
        self.pB_orderDispatched.setEnabled(True)

    def pB_order_dispatched_clicked(self):
        pi.logger.debug("Order Dispatched Button clicked")
        # Find the document with "processing" status and update it to "order_confirmed"
        plutito_ref = self.pluto_app.db.collection('plutito')
        query = plutito_ref.where('ordering_state', '==',  'Confirmed!').limit(1)
        results = query.stream()
        for doc in results:
            self.pluto_app.update_delivery_status(doc.id, "Dispatched!")
        self.pB_orderDispatched.setChecked(False)
        self.pB_orderDispatched.setEnabled(False)
        self.pB_orderDelivered.setEnabled(True)

    def pB_order_cancelled_clicked(self):
        pi.logger.debug("Order Cancelled Button clicked")
        # Find the document with "processing" status and update it to "order_confirmed"
        plutito_ref = self.pluto_app.db.collection('plutito')
        query = plutito_ref.where('ordering_state', '==', ['Confirmed!', 'Dispatched!', 'processing']).limit(1)
        results = query.stream()
        for doc in results:
            self.pluto_app.update_delivery_status(doc.id, "Cancelled!")
        self.pB_orderCancelled.setChecked(False)
        self.pB_orderConfirmed.setEnabled(True)
        self.pB_orderDispatched.setEnabled(False)
        self.pB_orderDelivered.setEnabled(False)
        self.pB_orderFinished.setEnabled(False)

    def order_delivered_clicked(self):
        pi.logger.debug("Order Delivered Button clicked")
        # Find the document with "processing" status and update it to "order_confirmed"
        plutito_ref = self.pluto_app.db.collection('plutito')
        query = plutito_ref.where('ordering_state', '==',  'Dispatched!').limit(1)
        results = query.stream()
        for doc in results:
            self.pluto_app.update_delivery_status(doc.id, "Delivered!")
        self.pB_orderDelivered.setChecked(False)
        self.pB_orderDelivered.setEnabled(False)
        self.pB_orderFinished.setEnabled(True)

    def pB_order_finished_clicked(self):
        pi.logger.debug("Order Fininshed Button clicked")
        # Find the document with "processing" status and update it to "order_confirmed"
        plutito_ref = self.pluto_app.db.collection('plutito')
        query = plutito_ref.where('ordering_state', '==',  'Delivered!').limit(1)
        results = query.stream()
        for doc in results:
            self.pluto_app.update_delivery_status(doc.id, "Finished!")
        self.pB_orderFinished.setChecked(False)
        self.pB_orderFinished.setEnabled(False)
        self.pB_orderConfirmed.setEnabled(True)

    def poll_controller(self):
        pygame.event.pump()
        if self.pluto_pico.control.get_controller_control():
            axis_0 = self.joystick.get_axis(0)
            axis_1 = self.joystick.get_axis(1)
            for i in range(self.joystick.get_numbuttons()):
                if self.joystick.get_button(i):
                    pi.logger.debug(f"Button {i} pressed")
            if axis_1 < -0.5:
                self.pluto_pico.control.go_forward()
            elif axis_1 > 0.5:
                self.pluto_pico.control.go_back()
            if axis_0 < -0.5:
                self.pluto_pico.control.turn_left()
            elif axis_0 > 0.5:
                self.pluto_pico.control.turn_right()

            start_button = self.joystick.get_button(6)  # Default Start button, adjust as needed
            if start_button:
                self.pluto_pico.control.set_handbrake(not self.pluto_pico.control.get_handbrake())

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if self.pluto_pico.control.get_keyboard_control():
                key = event.text().upper()
                if key == self.pluto_pico.control.key_mappings['handbrake']:
                    self.pluto_pico.control.set_handbrake(not self.pluto_pico.control.get_handbrake())
                elif key == self.pluto_pico.control.key_mappings['forward']:
                    self.pluto_pico.control.go_forward()
                elif key == self.pluto_pico.control.key_mappings['back']:
                    self.pluto_pico.control.go_back()
                elif key == self.pluto_pico.control.key_mappings['left']:
                    self.pluto_pico.control.turn_left()
                elif key == self.pluto_pico.control.key_mappings['right']:
                    self.pluto_pico.control.turn_right()
                else:
                    for i in range(8):
                        if key == self.pluto_pico.control.key_mappings[f'relay_{i}']:
                            self.pluto_pico.relays.toggle_relay(i)
                            break
                return True
        return super().eventFilter(obj, event)

    def update_sensor_values(self):
        """Update the distance sensor readings."""
        # EM-BTN
        self.tE_status_info.setText(self.pluto_pico.em_btn.get_state(False))
        # Temperatures
        self.tE_temp_sensor_0_temp.setText(self.pluto_pico.temperature.get_temperature_t0(False) + " °C")
        self.tE_temp_sensor_1_temp.setText(self.pluto_pico.temperature.get_temperature_t1(False) + " °C")
        self.tE_temp_sensor_2_temp.setText(self.pluto_pico.temperature.get_temperature_t2(False) + " °C")
        # Motors
        motors_speed = self.pluto_pico.control.motors.get_motors_speed_with_direction(False)
        self.tE_motor_1_speed.setText(motors_speed[0] + " %")
        self.tE_motor_2_speed.setText(motors_speed[1] + " %")
        # Proximity
        distances = self.pluto_pico.proximity.get_distance_sensor(False)
        self.tE_prox_sensor_0_distance.setText(distances[0] + " mm")
        self.tE_prox_sensor_1_distance.setText(distances[1] + " mm")
        self.tE_prox_sensor_2_distance.setText(distances[2] + " mm")
        self.tE_prox_sensor_3_distance.setText(distances[3] + " mm")
        # ADS1115
        self.tE_cell_1_voltage.setText(str(self.pluto_pico.batteries.get_batteries_b0(False)) + " V")
        self.tE_cell_2_voltage.setText(str(self.pluto_pico.batteries.get_batteries_b1(False)) + " V")
        self.tE_cell_3_voltage.setText(str(self.pluto_pico.batteries.get_batteries_b2(False)) + " V")
        self.tE_cell_4_voltage.setText(str(self.pluto_pico.batteries.get_batteries_b3(False)) + " V")


def create_window():
    """
    Creates the Qt Application Window and starts the event loop.
    """
    pi.logger.debug("Creating Qt Application Window")
    app = QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec())
