#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color, Button
from pybricks.robotics import DriveBase
from pybricks.tools import wait

# =============================================================================
# ⚙️ YOUR CALIBRATION DATA
# =============================================================================

# THRESHOLDS
BLACK_VAL = 10   
WHITE_VAL = 80   
THRESHOLD = (BLACK_VAL + WHITE_VAL) / 2

# SPEED SETTINGS
DRIVE_SPEED = 25   
TURN_GAIN = 1.2     

# =============================================================================
# 🔌 SETUP (FIXED ERROR HERE)
# =============================================================================
ev3 = EV3Brick()

# 1. Set Volume Separately (Fixes the crash)
ev3.speaker.set_volume(100)

# 2. Set Voice Options
ev3.speaker.set_speech_options(speed=80, pitch=60)

# Motors
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
line_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🏃 MAIN TEST LOOP
# =============================================================================

ev3.speaker.say("Sensor Check")
print("--- PRESS CENTER BUTTON TO START DRIVING ---")

# PART 1: PRINT NUMBERS
while Button.CENTER not in ev3.buttons.pressed():
    ref = line_sensor.reflection()
    col = line_sensor.color()
    print("Reflect:", ref, "| Color:", col)
    wait(100)

# PART 2: LINE FOLLOWING
ev3.speaker.say("Starting Line Follower")
wait(1000)

while True:
    seen_color = line_sensor.color()
    current_reflect = line_sensor.reflection()

    # CHECK FOR STATIONS
    if seen_color == Color.GREEN:
        robot.stop()
        ev3.speaker.say("Green Station")
        wait(2000)
        robot.drive(DRIVE_SPEED, 0)

    elif seen_color == Color.YELLOW:
        robot.stop()
        ev3.speaker.say("Yellow Station")
        wait(2000)
        robot.drive(DRIVE_SPEED, 0)

    elif seen_color == Color.RED: 
        robot.stop()
        ev3.speaker.say("Orange Station")
        wait(2000)
        robot.drive(DRIVE_SPEED, 0)

    # LINE FOLLOWER
    else:
        deviation = current_reflect - THRESHOLD
        turn_rate = deviation * TURN_GAIN
        robot.drive(DRIVE_SPEED, turn_rate)