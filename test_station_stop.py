#!/usr/bin/env pybricks-micropython
from pybricks.parameters import Color, Button
from pybricks.tools import wait
import hardware
import config

print("--- 3 STATION TEST + LOGS ---")
print("Press CENTER to stop")

# Counters
count_stn1 = 0
count_stn2 = 0 # Covers both Red & Orange stations

# Start Green Light
hardware.ev3.light.on(Color.GREEN)

while True:
    # 1. READ SENSORS
    ref = hardware.line_sensor.reflection()
    col = hardware.line_sensor.color()
    
    # 2. LOGGING (Added)
    # Shows: Color | Reflection | Count Stn1 | Count Stn2
    print(str(col) + " | Ref: " + str(ref) + "% | S1:" + str(count_stn1) + " S2:" + str(count_stn2))
    
    # 3. CHECK FOR STATION 1 (Blue)
    # Logic: Color matches Config AND Reflection matches Config Range
    is_stn1_color = (col in config.STATION_1_COLOR)
    is_stn1_range = (config.STATION_1_MIN <= ref <= config.STATION_1_MAX)
    
    if is_stn1_color and is_stn1_range:
        count_stn1 += 1
        count_stn2 = 0 
    
    # 4. CHECK FOR STATION 2 & 3 (Red)
    # We use Station 2 config, but it covers Station 3 too since they are the same (Red)
    elif (col in config.STATION_2_COLOR) and (config.STATION_2_MIN <= ref <= config.STATION_2_MAX):
        count_stn2 += 1
        count_stn1 = 0
        
    # 5. RESET IF NOTHING
    else:
        count_stn1 = 0
        count_stn2 = 0
        
    # 6. STOP ACTION (If confirmed 3 times)
    if count_stn1 >= 3:
        hardware.robot.stop()
        hardware.ev3.speaker.say("Plastic Station")
        print(">>> STOPPED: Station 1 (Blue)")
        wait(2000) # Pause
        count_stn1 = 0 
        hardware.robot.reset()
        
    elif count_stn2 >= 5:
        hardware.robot.stop()
        hardware.ev3.speaker.say("Red Station") 
        print(">>> STOPPED: Station 2 or 3 (Red)")
        wait(2000)
        count_stn2 = 0
        hardware.robot.reset()

    # 7. SMOOTH LINE FOLLOWING
    turn_rate = (ref - config.THRESHOLD) * config.TURN_GAIN
    hardware.robot.drive(config.DRIVE_SPEED, turn_rate)
    
    # 8. EXIT
    if Button.CENTER in hardware.ev3.buttons.pressed():
        break
    
    wait(10)

hardware.robot.stop()
print("Test Ended.")