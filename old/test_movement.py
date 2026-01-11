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
line_sensor = ColorSensor(Port.S3)
clamp_sensor = ColorSensor(Port.S2)
distance_sensor = UltrasonicSensor(Port.S1)

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
CLAMP_OPEN_ANGLE = -60

# Corner Logic
WHITE_THRESHOLD = 75 
VALID_WHITE_DIST = 50   
CORNER_COOLDOWN = 200   
CONFIRM_THRESHOLD = 5

# Station Order Definition
STATION_ORDER = ["Plastic Station", "Other Station", "Paper Station"]

ITEM_TO_STATION = {
    "Plastic": "Plastic Station",
    "Paper": "Paper Station",
    "None": "Other Station"
}

# Trash Database
TRASH_DB = [
    ("None",    0, 5,   [None, Color.BLACK]),
    ("Plastic", 6, 100, [Color.BLACK, Color.BROWN, Color.YELLOW, Color.BLUE]),
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

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

def check_station_logic(target_name, color, reflection):
    if target_name == "Plastic Station": 
        return color == Color.BLUE and 18 <= reflection <= 30
    elif target_name == "Other Station": 
        return color == Color.WHITE and 45 <= reflection <= 65
    elif target_name == "Paper Station": 
        return color == Color.RED and reflection >= 80
    return False

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
        return "Plastic Station"
    if color == Color.WHITE and 48 <= reflection <= 60:
        return "Other Station"
    if color == Color.RED and reflection >= 95:
        return "Paper Station"
    return None

# State variables
corners_passed = 0
white_start_dist = -1
last_corner_finish_dist = -200
next_station = 1
confirm_count = 0
found_stations = []
held_item = None
target_station = None

try:
    initialize()
    print("{:<10} | {:<10} | {:<10} | {:<10} | {:<15}".format("Dist", "Color", "Ref", "Amb", "Status"))
    print("-" * 65)
    
    while True:
        # Object Detection (Triggered if something is within 100mm)
        if distance_sensor.distance() < 100 and held_item is None:
            held_item = pick_up()
            target_station = ITEM_TO_STATION[held_item]

        ref = line_sensor.reflection()
        col = line_sensor.color()
        amb = line_sensor.ambient()
        curr_dist = robot.distance()
        detected = get_station_name(col, ref)
        
        # Navigation
        if col == Color.RED or col == Color.BLUE:
            robot.drive(DRIVE_SPEED, 0)
            status_text = "STRAIGHT"
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
            
            # Integrated logic for delivering held items
            is_target = False
            if target_station:
                is_target = check_station_logic(target_station, col, ref)

            if confirm_count >= CONFIRM_THRESHOLD:
                robot.stop()
                ev3.speaker.say(detected)
                
                if is_target:
                    ev3.speaker.say("Target reached")
                    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
                    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
                    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
                    held_item = None
                    target_station = None

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