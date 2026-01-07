#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Button, Stop
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# Setup
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2)
line_sensor = ColorSensor(Port.S3)
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)
mission_timer = StopWatch()

# Constants
THRESHOLD = 44       
DRIVE_SPEED = 50    
TURN_GAIN = -1.5    
WHITE_THRESHOLD = 75 
VALID_WHITE_DIST = 50   
CORNER_COOLDOWN = 200   
CONFIRM_THRESHOLD = 5
SLOW_PACE = 30  
ARM_SPEED = 200
ARM_SAFE_POS = -260
ARM_DOWN_POS = 0
CLAMP_SPEED = 200
CLAMP_FORCE = 72
CLAMP_OPEN_ANGLE = -70

# Trash Database
TRASH_DB = [
    ("None",    0, 5,   [None, Color.BLACK]),
    ("Plastic", 6, 100, [Color.BLACK, Color.BROWN, Color.YELLOW, Color.BLUE]),
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

ITEM_TO_STATION = {
    "Plastic": "Plastic Station",
    "Paper": "Paper Station",
    "None": "Other Station"
}

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

def identify_trash():
    final_decision = "None"
    for i in range(5):
        col, ref = clamp_sensor.color(), clamp_sensor.reflection()
        for name, mi, ma, colors in TRASH_DB:
            if mi <= ref <= ma and col in colors:
                final_decision = name
        wait(200)
    return final_decision

def pick_up():
    robot.stop() 
    ev3.speaker.say("Object Detected")
    robot.straight(30) 
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    item = identify_trash()
    ev3.speaker.say(item)
    return item

def unload_sequence():
    robot.stop()
    # Turn right 90 degrees
    robot.turn(90)
    # Go forward until ultrasonic < 30mm (3cm)
    while obstacle_sensor.distance() > 30:
        robot.drive(SLOW_PACE, 0)
        wait(10)
    robot.stop()
    # Open clamp while lifting (simultaneous)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS, wait=False)
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
    # Go back slowly
    robot.straight(-100)
    # Turn left to return to line
    robot.turn(-90)

def check_station_logic(target_name, color, reflection):
    if target_name == "Plastic Station": # Dark Blue
        return color == Color.BLUE and 18 <= reflection <= 25
    elif target_name == "Paper Station": # Light Green
        return color == Color.WHITE and 48 <= reflection <= 60
    elif target_name == "Other Station": # Orange
        return color == Color.RED and reflection >= 95
    return False

# Mission State
current_item = "None"
holding_object = False
corners_passed = 0
white_start_dist = -1
last_corner_finish_dist = -200
confirm_count = 0

try:
    initialize()
    
    while True:
        ref = line_sensor.reflection()
        col = line_sensor.color()
        obj_dist = obstacle_sensor.distance()
        curr_dist = robot.distance()
        
        # --- 1. TRASH DETECTION ---
        if not holding_object and obj_dist < 50:
            current_item = pick_up()
            holding_object = True
            continue 

        # --- 2. NAVIGATION ---
        if col == Color.RED:
            robot.drive(DRIVE_SPEED, 0)
        else:
            turn_rate = (ref - THRESHOLD) * TURN_GAIN
            robot.drive(DRIVE_SPEED, turn_rate)

        # --- 3. STATION DETECTION ---
        # Logic for Plastic (Blue), Paper (Green), Other (Orange)
        stations = ["Plastic Station", "Paper Station", "Other Station"]
        for station in stations:
            if check_station_logic(station, col, ref):
                confirm_count += 1
                if confirm_count >= CONFIRM_THRESHOLD:
                    robot.stop()
                    ev3.speaker.say(station)
                    
                    target_for_item = ITEM_TO_STATION.get(current_item, "Other Station")
                    
                    if holding_object and station == target_for_item:
                        unload_sequence()
                        holding_object = False
                        current_item = "None"
                    else:
                        # Just passing by: move 80mm forward to clear station marker
                        robot.straight(80)
                    
                    confirm_count = 0
                    break
        else:
            confirm_count = 0
        
        # --- 4. CORNER COUNTING ---
        if mission_timer.time() > 5000:
            if (curr_dist - last_corner_finish_dist > CORNER_COOLDOWN):
                if ref > WHITE_THRESHOLD:
                    if white_start_dist == -1: white_start_dist = curr_dist 
                    if (curr_dist - white_start_dist) >= VALID_WHITE_DIST:
                        corners_passed += 1
                        ev3.speaker.beep()
                        last_corner_finish_dist = curr_dist
                        white_start_dist = -1 
                else:
                    white_start_dist = -1 

        if Button.CENTER in ev3.buttons.pressed(): break
        wait(10)

finally:
    shutdown()