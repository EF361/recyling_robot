#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# Setup
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
line_sensor = ColorSensor(Port.S3)
distance_sensor = UltrasonicSensor(Port.S1)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# Constants
DRIVE_SPEED = 80
SLOW_PACE = 40
TURN_SPEED_SLOW = 50 
CLAMP_SPEED = 200
CLAMP_OPEN_ANGLE = -60
ARM_SPEED = 200
ARM_HIGH_POS = -270 # Adjusted to keep the arm high

# Configure turn speed
robot.settings(turn_rate=TURN_SPEED_SLOW)

try:
    # 0. Initial Setup: Raise arm to high position
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_HIGH_POS, then=Stop.HOLD)

    # 1. Drive until Red Color (Orange Station) is detected
    while line_sensor.color() != Color.RED:
        robot.drive(DRIVE_SPEED, 0)
        wait(10)
    
    robot.stop()
    ev3.speaker.beep()
    
    # 2. Turn 90 degrees slowly to the right
    robot.straight(20)
    robot.turn(150)
    wait(500)

    # 3. Move forward slowly until ultrasonic sensor < 2 cm (20mm)
    robot.drive(SLOW_PACE, 0)
    while distance_sensor.distance() > 50:
        robot.drive(30, 0)
        wait(10)
    
    robot.stop()

    # 4. Open the clamp (Arm stays at ARM_HIGH_POS)
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE, then=Stop.BRAKE)
    ev3.speaker.say("Task Complete")

finally:
    robot.stop()
    left_motor.stop()
    right_motor.stop()