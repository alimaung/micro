# Trinamic Control

A Python library for controlling Trinamic stepper motor controllers, ported from VB.NET code.

## Overview

This library provides a Python interface to control Trinamic stepper motor controllers using the TMCL (Trinamic Motion Control Language) protocol over serial communication. It was ported from a VB.NET application.

## Features

- Motor control (speed, acceleration, current)
- I/O control (vacuum, LED, magnet)
- Sensor reading (light sensor, voltage)
- Configuration management

## Project Structure

```
trinamic_control/
├── config/
│   └── trinamic.ini        # Configuration file
├── examples/
│   ├── basic_movement.py   # Example for motor movement
│   └── io_control_example.py  # Example for I/O control
└── src/
    ├── __init__.py         # Package initialization
    ├── trinamic_controller.py  # Main controller class
    ├── motor_control.py    # Motor control functions
    ├── io_control.py       # I/O control functions
    └── config_manager.py   # Configuration management
```

## Usage

### Basic Motor Control

```python
from trinamic_control.src.trinamic_controller import TrinamicController
from trinamic_control.src.motor_control import MotorControl

# Create and connect to controller
controller = TrinamicController(port='COM3', baudrate=9600)
controller.connect()

# Create motor control interface
motor = MotorControl(controller)

# Configure motor
motor.set_motor_resolution(1, 4)  # Motor 1, 1/4 microstepping
motor.set_max_current(1, 50)      # Motor 1, 50% current

# Move motor
motor.move_motor(1, 1000)  # Move motor 1, 1000 steps

# Wait for motor to stop
while motor.is_motor_running(1):
    time.sleep(0.1)

# Disconnect
controller.disconnect()
```

### I/O Control

```python
from trinamic_control.src.trinamic_controller import TrinamicController
from trinamic_control.src.io_control import IOControl

# Create and connect to controller
controller = TrinamicController(port='COM3', baudrate=9600)
controller.connect()

# Create I/O control interface
io = IOControl(controller)

# Control outputs
io.led_on()
io.vacuum_on()

# Read inputs
if io.is_lid_closed():
    print("Lid is closed")

# Disconnect
controller.disconnect()
```

## Requirements

- Python 3.6+
- pyserial

## Installation

```
pip install pyserial
```

Clone this repository or copy the files to your project.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 