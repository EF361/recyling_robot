#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Color, Button  # <--- FIXED IMPORTS
from pybricks.tools import wait
import hardware
import config

print("--- LINE FOLLOW TEST ---")
print("Press CENTER to stop")

# Start Green Light
hardware.ev3.light.on(Color.GREEN)

while True:
    # 1. Read Sensor
    ref = hardware.line_sensor.reflection()
    
    # 2. Calculate Turn
    # If ref is high (white), turn left. If low (black), turn right.
    turn_rate = (ref - config.THRESHOLD) * config.TURN_GAIN
    
    # 3. Drive
    hardware.robot.drive(config.DRIVE_SPEED, turn_rate)
    
    # 4. Stop if button pressed
    if Button.CENTER in hardware.ev3.buttons.pressed():
        break
    
    wait(10)

hardware.robot.stop()
print("Stopped.")