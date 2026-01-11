#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Button, Stop
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# Setup
# Setup - Ports updated based on user hardware
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
obstacle_sensor = UltrasonicSensor(Port.S1)  # Port 1
clamp_sensor = ColorSensor(Port.S2)         # Port 2
line_sensor = ColorSensor(Port.S3)          # Port 3
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)
mission_timer = StopWatch()

# Constants
ARM_SPEED = 200
ARM_HIGH_POS = -270
CLAMP_SPEED = 200
CLAMP_OPEN_ANGLE = -60

def open_clamp():
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_HIGH_POS, then=Stop.HOLD)
    wait(6000)
# Execution
open_clamp()