# hardware.py
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port
from pybricks.robotics import DriveBase
from pybricks.parameters import Button

# Initialize Brick
ev3 = EV3Brick()

# Initialize Motors
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

# Initialize Sensors
obstacle_sensor = UltrasonicSensor(Port.S1)  # Port 1
clamp_sensor = ColorSensor(Port.S2)         # Port 2
line_sensor = ColorSensor(Port.S3)          # Port 3

# Initialize DriveBase
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)