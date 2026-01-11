#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Button
from pybricks.tools import wait
import hardware
import actions

print("--- ARM & CATEGORY CALIBRATION ---")
print("1. Put object -> Robot Pick -> ID")
print("2. READ TERMINAL FOR COLOR/REF VALUES")
print("3. AFTER DROP: Press CENTER to reset")

# Initialize once
actions.initialize()

while True:
    dist = hardware.obstacle_sensor.distance()
    
    # Print distance so you know if you are in the "Blind Spot" (<30mm)
    # \r makes it print on the same line to keep terminal clean
    print("Dist: " + str(dist) + "mm   ", end='\r')
    
    # Trigger if object is visible (Safe range: 30mm - 60mm)
    if dist < 60:
        print("\n\n>> Object detected! Picking up...")
        
        # Get Item Name AND Sensor Readings
        item, col, ref = actions.pick_and_drop()
        
        print("-" * 30)
        print(">>> RESULT: " + str(item))
        print(">>> DATA FOR CONFIG.PY:")
        print("    Color:      " + str(col))
        print("    Reflection: " + str(ref) + "%")
        print("-" * 30)
        
        print(">>> REMOVE ITEM & PRESS CENTER TO CONTINUE")
        
        # Wait for MANUAL confirmation to restart
        while Button.CENTER not in hardware.ev3.buttons.pressed():
            wait(20)
        
        # Wait for button release
        while Button.CENTER in hardware.ev3.buttons.pressed():
            wait(20)
            
        print(">>> Ready for next object...")
        wait(1000)
    
    # Standard wait
    wait(100)

actions.shutdown()