#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color, Button
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# =============================================================================
# ⚙️ YOUR CALIBRATION DATA (Auto-filled based on your list)
# =============================================================================

# PORT CONFIGURATION
# Port 1: Ultrasonic
# Port 2: Clamp Light Sensor (Trash ID)
# Port 3: Line Follower Light Sensor (Floor)
# Port A: Clamp Open/Close
# Port B: Clamp Up/Down
# Port C: Right Wheel
# Port D: Left Wheel

# THRESHOLDS (Calculated from your environment)
# You didn't give "Black Line" or "White Floor" specifically, 
# so I am estimating based on your "Water Bottle" (Dark) and "Paper" (Bright) data.
BLACK_VAL = 10   # Est. from your "Water Bottle" reflect (8-10)
WHITE_VAL = 80   # Est. from your "Yellow" reflect (100) or clean floor
THRESHOLD = (BLACK_VAL + WHITE_VAL) / 2

# SPEED SETTINGS
DRIVE_SPEED = 100   # mm/s (Slow for testing)
TURN_GAIN = 1.2     # Steering sensitivity

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()

# Voice Settings (Slower = Clearer)
ev3.speaker.set_speech_options(volume=100, speed=80, pitch=60)

# Motors (Using your C=Right, D=Left)
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)

# Sensor (Port 3 for Line Following)
line_sensor = ColorSensor(Port.S3)

# DriveBase
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🏃 MAIN TEST LOOP
# =============================================================================

ev3.speaker.say("Sensor Check")
print("--- PRESS CENTER BUTTON TO START DRIVING ---")

# PART 1: PRINT NUMBERS (Debug Mode)
# Use this to verify your Black Line is ~10 and Floor is >50
while Button.CENTER not in ev3.buttons.pressed():
    ref = line_sensor.reflection()
    col = line_sensor.color()
    print("Reflect:", ref, "| Color:", col)
    wait(100)

# PART 2: LINE FOLLOWING & DETECTION
ev3.speaker.say("Starting Line Follower")
wait(1000)

while True:
    # 1. READ SENSORS
    # We read both Color (for Stations) and Reflection (for steering)
    seen_color = line_sensor.color()
    current_reflect = line_sensor.reflection()

    # 2. CHECK FOR STATIONS (Using your Data)
    # Priority: Stop if we see a station color!
    
    if seen_color == Color.GREEN:  # Your "Color 3"
        robot.stop()
        ev3.speaker.say("Green Station Detected")
        wait(2000) # Wait so we don't say it 100 times
        robot.drive(DRIVE_SPEED, 0) # Start moving again

    elif seen_color == Color.YELLOW: # Your "Color 4"
        robot.stop()
        ev3.speaker.say("Yellow Station Detected")
        wait(2000)
        robot.drive(DRIVE_SPEED, 0)

    elif seen_color == Color.RED:    # Your "Color 5" (Orange)
        robot.stop()
        ev3.speaker.say("Orange Station Detected")
        wait(2000)
        robot.drive(DRIVE_SPEED, 0)

    # 3. LINE FOLLOWER (Standard Logic)
    else:
        # Calculate steering
        deviation = current_reflect - THRESHOLD
        turn_rate = deviation * TURN_GAIN
        
        # Drive
        robot.drive(DRIVE_SPEED, turn_rate)