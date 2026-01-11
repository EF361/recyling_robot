#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Button  # <--- Added this import
from pybricks.tools import wait
import hardware 

print("--- SENSOR TEST ---")
print("Press CENTER to exit")

while True:
    # 1. Read all sensors
    col = hardware.line_sensor.color()
    ref = hardware.line_sensor.reflection()
    dist = hardware.obstacle_sensor.distance()
    
    # 2. Print them clearly
    print("Color: " + str(col) + " | Refl: " + str(ref) + "% | Dist: " + str(dist) + "mm")
    
    wait(200)
    
    # 3. Exit condition
    # We now use 'Button.CENTER' directly, which comes from the import above
    if Button.CENTER in hardware.ev3.buttons.pressed():
        break