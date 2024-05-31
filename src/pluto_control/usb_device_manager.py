# device_manager.py

import serial
import serial.tools.list_ports


def list_usb_devices():
    """List all connected USB devices."""
    ports = serial.tools.list_ports.comports()
    return ports


def connect_to_device(port, baud_rate=9600):
    """Connect to a given serial port."""
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        return ser
    except serial.SerialException as e:
        print(f"Error connecting to port {port}: {str(e)}")
        return None


def send_command(ser, command):
    """Send a command to the connected device."""
    if ser is not None and ser.isOpen():
        ser.write((command + "\n").encode("utf-8"))  # Ensure command is properly encoded
        response = ser.readline().decode("utf-8").strip()  # Read and decode response
        return response
    else:
        return "Not connected."
