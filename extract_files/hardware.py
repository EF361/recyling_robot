from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase

ev3 = EV3Brick()

# Motors
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

# Sensors
obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2)
line_sensor = ColorSensor(Port.S3)

# DriveBase setup
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)