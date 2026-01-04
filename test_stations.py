#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================
# Line Following (Standard)
THRESHOLD = 45       
DRIVE_SPEED = 50     
TURN_GAIN = -1.2     

# Corner Sensitivity
# If the robot steers harder than this, we mark it as a "CORNER" in the log.
CORNER_THRESHOLD = 40 

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
# Sensors
line_sensor = ColorSensor(Port.S3)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🚀 DATA LOGGING LOOP
# =============================================================================
ev3.speaker.beep()
print("--------------------------------------------------")
print("DATA LOG STARTING - 3 ROUNDS")
print("Format: Color | Refl | Amb | TurnRate | Notes")
print("--------------------------------------------------")

while True:
    # 1. Exit Button
    if Button.CENTER in ev3.buttons.pressed():
        break

    # 2. Read Sensors
    col_name = line_sensor.color()
    refl = line_sensor.reflection()
    amb = line_sensor.ambient()

    # 3. Calculate Steering (Line Following)
    deviation = refl - THRESHOLD
    turn_rate = deviation * TURN_GAIN
    
    # 4. Drive
    robot.drive(DRIVE_SPEED, turn_rate)

    # 5. Detect Special Events for Log
    note = ""
    
    # Check for CORNER (High turning value)
    if abs(turn_rate) > CORNER_THRESHOLD:
        note += "[CORNER] "
        
    # Check for COLORS (Potential Stations)
    # Filter out common floor/line readings to highlight the interesting stuff
    if col_name not in [Color.BLACK, Color.WHITE, None]:
        note += "[COLOR DETECTED!] "
    
    # Check specifically for the "Green on Black" glitch
    if (col_name == Color.GREEN or col_name == Color.BLUE) and (refl < 25):
         note += "[GREEN/BLUE LOW REFL] "

    # 6. Print Data (CSV Style)
    # converting color to string to make it readable
    print("{:<12} | {:<4} | {:<4} | {:<4} | {}".format(
        str(col_name), refl, amb, int(turn_rate), note
    ))

    # 7. Short Wait (Avoid flooding terminal too fast)
    wait(50)

# Stop
robot.stop()
print("--------------------------------------------------")
print("LOG FINISHED")
print("--------------------------------------------------")