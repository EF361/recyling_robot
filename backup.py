#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor
from pybricks.parameters import Port, Color, Button, Stop
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# Setup
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
line_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)
mission_timer = StopWatch()

# Constants
THRESHOLD = 44       
DRIVE_SPEED = 50    
TURN_GAIN = -1.2    
ARM_SPEED = 200
ARM_SAFE_POS = -260
ARM_DOWN_POS = 0
CLAMP_SPEED = 200
CLAMP_FORCE = 72
SLOW_PACE = 30 

# Corner Logic
WHITE_THRESHOLD = 75 
VALID_WHITE_DIST = 50   
CORNER_COOLDOWN = 200   
CONFIRM_THRESHOLD = 5

def initialize():
    try:
        ev3.screen.load_image('logo.png')
    except:
        ev3.screen.print("No Logo Found")
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS, then=Stop.BRAKE)
    clamp.run_until_stalled(-CLAMP_SPEED, duty_limit=40)
    clamp.run_until_stalled(CLAMP_SPEED, duty_limit=40)
    clamp.reset_angle(0)
    clamp.run_target(CLAMP_SPEED, -5, then=Stop.COAST)
    robot.reset()
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Ready")
    while Button.CENTER not in ev3.buttons.pressed(): wait(20)
    while Button.CENTER in ev3.buttons.pressed(): wait(20)

def shutdown():
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutdown")
    clamp.run_until_stalled(CLAMP_SPEED, duty_limit=CLAMP_FORCE)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    ev3.screen.clear()
    left_motor.stop()
    right_motor.stop()
    ev3.speaker.beep()

def get_station_name(color, reflection):
    if color == Color.BLUE and 18 <= reflection <= 25:
        return "Dark Blue Station"
    if color == Color.WHITE and 48 <= reflection <= 60:
        return "Light Green Station"
    if color == Color.RED and reflection >= 95:
        return "Orange Station"
    return None

# State variables
corners_passed = 0
white_start_dist = -1
last_corner_finish_dist = -200
next_station = 1
confirm_count = 0
found_stations = []

try:
    initialize()
    print("{:<10} | {:<10} | {:<10} | {:<10} | {:<15}".format("Dist", "Color", "Ref", "Amb", "Status"))
    print("-" * 65)
    
    while True:
        ref = line_sensor.reflection()
        col = line_sensor.color()
        amb = line_sensor.ambient()
        curr_dist = robot.distance()
        detected = get_station_name(col, ref)
        
        # Navigation
        if col == Color.RED:
            robot.drive(DRIVE_SPEED, 0)
            status_text = "RED-STRAIGHT"
        else:
            turn_rate = (ref - THRESHOLD) * TURN_GAIN
            robot.drive(DRIVE_SPEED, turn_rate)
            status_text = "Following"

        # Corner Counting
        if mission_timer.time() > 5000 and next_station == 1:
            if (curr_dist - last_corner_finish_dist > CORNER_COOLDOWN):
                if ref > WHITE_THRESHOLD:
                    if white_start_dist == -1: white_start_dist = curr_dist 
                    if (curr_dist - white_start_dist) >= VALID_WHITE_DIST:
                        corners_passed += 1
                        ev3.speaker.beep()
                        last_corner_finish_dist = curr_dist
                        white_start_dist = -1 
                        print("\n[#] CORNER {} CONFIRMED\n".format(corners_passed))
                else:
                    white_start_dist = -1 

        # Station Detection
        if detected and (detected not in found_stations):
            confirm_count += 1
            status_text = "Confirming"
            if confirm_count >= CONFIRM_THRESHOLD:
                robot.stop()
                ev3.speaker.say(detected)
                robot.settings(straight_speed=SLOW_PACE)
                robot.straight(80)
                print("\n[!] STATION: {} confirmed. Moving 80mm. Stop 2s.\n".format(detected))
                found_stations.append(detected)
                wait(2000)
                confirm_count = 0
        else:
            confirm_count = 0
            if not detected: found_stations = []

        print("{:<10.1f} | {:<10} | {:<10} | {:<10} | {:<15}".format(curr_dist, str(col), ref, amb, status_text))
        wait(10)
        if Button.CENTER in ev3.buttons.pressed(): break

finally:
    shutdown()