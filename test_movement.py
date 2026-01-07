#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port
from pybricks.tools import wait
from pybricks.robotics import DriveBase

ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
line_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

DRIVE_SPEED = 50 

print("{:<15} | {:<12} | {:<12} | {:<12}".format("Distance (mm)", "Color", "Reflection", "Ambient"))
print("-" * 60)

robot.reset()
robot.drive(DRIVE_SPEED, 0)

try:
    while robot.distance() < 2000:
        dist = robot.distance()
        col = str(line_sensor.color())
        ref = line_sensor.reflection()
        amb = line_sensor.ambient()

        print("{:<15.1f} | {:<12} | {:<12} | {:<12}".format(dist, col, ref, amb))
        
        wait(100)
finally:
    robot.stop()
    print("Logging Finished.")