import time

from serial_handler import SerialHandler

class PlutoPico:
    def __init__(self, config_file, existing_serial_handler):
        self.config = config_file
        self.serial_handler = existing_serial_handler
        self.motors = []
        self.initialize_motors()

    def initialize_motors(self):
        for motor_number in range(1, 3):  # Assuming we have motor1 and motor2
            motor_config = self.load_motor_config(motor_number)
            motor = self.Motor(motor_number, motor_config, self.send_command)
            self.motors.append(motor)

    def load_motor_config(self, motor_number):
        section = f'MOTOR_{motor_number}_CONFIG'
        return {
            'direction': self.config.getint(section, 'direction', fallback=0),
            'max_speed': self.config.getint(section, 'max_speed', fallback=50),
            'accel_rate': self.config.getint(section, 'accel_step_size', fallback=5),
            'brake_rate': self.config.getint(section, 'brake_step_size', fallback=5),
            'accel_delay': self.config.getint(section, 'accel_step_delay', fallback=100),
            'brake_delay': self.config.getint(section, 'brake_step_delay', fallback=100),
        }

    def send_command(self, command):
        # Use the SerialHandler instance to send the command
        command_with_newline = command + "\n"
        self.serial_handler.write(command_with_newline.encode('utf-8'))
        time.sleep(1)

    class Motor:
        def __init__(self, motor_number, config, send_command_func):
            self.motor_number = motor_number
            self.config = config
            self.send_command = send_command_func

        def set_direction(self, state):
            command = f"motor{self.motor_number} set-dir {state}"
            self.send_command(command)

        # This will set the motor on :D
        def set_max_speed(self, value):
            command = f"motor{self.motor_number} set-speed {value}"
            self.send_command(command)

        def set_accel_rate(self, value):
            command = f"motor{self.motor_number} config-acc-rate {value}"
            self.send_command(command)

        def set_brake_rate(self, value):
            command = f"motor{self.motor_number} config-brak-rate {value}"
            self.send_command(command)

        def set_accel_delay(self, value):
            command = f"motor{self.motor_number} config-acc-rate-delay {value}ms"
            self.send_command(command)

        def set_brake_delay(self, value):
            command = f"motor{self.motor_number} config-brak-rate-delay {value}ms"
            self.send_command(command)

        def initialize(self):
            self.set_direction(self.config['direction'])
            self.set_max_speed(self.config['max_speed'])
            self.set_accel_rate(self.config['accel_rate'])
            self.set_brake_rate(self.config['brake_rate'])
            self.set_accel_delay(self.config['accel_delay'])
            self.set_brake_delay(self.config['brake_delay'])

    def initialize(self):
        for motor in self.motors:
            motor.initialize()

# Example usage:
if __name__ == "__main__":
    from configparser import ConfigParser

    # Load configuration (this would normally be loaded from a file)
    config = ConfigParser()
    config.read('pluto_config.ini')

    # Initialize the SerialHandler
    def log_callback(message, direction):
        print(f"{direction.upper()}: {message}")

    serial_handler = SerialHandler(log_callback)
    serial_handler.connect('/dev/ttyUSB0')  # Update this with your actual port

    # Initialize PlutoPico with the loaded configuration and SerialHandler
    pluto_pico = PlutoPico(config, serial_handler)
    pluto_pico.initialize()
