#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Color, Button, Stop
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

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
THRESHOLD = 44       
DRIVE_SPEED = 50    
TURN_GAIN = -1.2    
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

def pick_and_drop():
    robot.stop() 
    wait(100) 
    ev3.speaker.say("Object")
    robot.drive(30, 0)
    wait(1000) 
    robot.stop()
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    item = identify_trash()
    ev3.speaker.say(item)
    if item != "None":
        wait(5000)
        clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
        wait(1000)
        clamp.run_until_stalled(CLAMP_SPEED, duty_limit=CLAMP_FORCE)
    else:
        clamp.run_until_stalled(CLAMP_SPEED, duty_limit=CLAMP_FORCE)

def check_station_logic(target_name, color, reflection):
    if target_name == "Dark Blue Station":
        return color == Color.BLUE and 18 <= reflection <= 25
    elif target_name == "Light Green Station":
        return color == Color.WHITE and 48 <= reflection <= 60
    elif target_name == "Orange Station":
        return color == Color.RED and reflection >= 95
    return False

# Mission State
STATION_SEQUENCE = ["Plastic Station", "Paper Station", "Other Station"]
current_target_idx = 0
corners_passed = 0
white_start_dist = -1
last_corner_finish_dist = -200
confirm_count = 0

try:
    initialize()
    print("{:<10} | {:<10} | {:<10} | {:<10} | {:<15}".format("Dist", "Color", "Ref", "Obj", "Status"))
    print("-" * 75)
    
    while True:
        target_station = STATION_SEQUENCE[current_target_idx % len(STATION_SEQUENCE)]
        ref = line_sensor.reflection()
        col = line_sensor.color()
        obj_dist = obstacle_sensor.distance()
        curr_dist = robot.distance()
        
        # --- 1. TRASH DETECTION ---
        if obj_dist < 50:
            pick_and_drop()
            robot.reset() 
            last_corner_finish_dist = -200
            continue 

        # --- 2. NAVIGATION ---
        if col == Color.RED:
            robot.drive(DRIVE_SPEED, 0)
            status_text = "RED-STRAIGHT"
        elif ref > THRESHOLD + 20: 
            robot.stop() 
            left_motor.run(-20)  
            right_motor.run(80)  
            status_text = "REV-LEFT"
        else:
            turn_rate = (ref - THRESHOLD) * TURN_GAIN
            robot.drive(DRIVE_SPEED, turn_rate)
            status_text = "FOLLOWING"

        # --- 3. CORNER COUNTING ---
        if mission_timer.time() > 5000:
            if (curr_dist - last_corner_finish_dist > CORNER_COOLDOWN):
                if ref > WHITE_THRESHOLD:
                    if white_start_dist == -1: white_start_dist = curr_dist 
                    if (curr_dist - white_start_dist) >= VALID_WHITE_DIST:
                        corners_passed += 1
                        ev3.speaker.beep()
                        last_corner_finish_dist = curr_dist
                        white_start_dist = -1 
                        print("\n[#] CORNER {} DETECTED\n".format(corners_passed))
                else:
                    white_start_dist = -1 

        # --- 4. STATION DETECTION ---
        if check_station_logic(target_station, col, ref):
            confirm_count += 1
            if confirm_count >= CONFIRM_THRESHOLD:
                robot.stop()
                ev3.speaker.say(target_station)
                robot.settings(straight_speed=SLOW_PACE)
                robot.straight(80)
                wait(2000)
                current_target_idx += 1
                confirm_count = 0
        else:
            confirm_count = 0

        # --- 5. PRINT READINGS ---
        print("{:<10.1f} | {:<10} | {:<10} | {:<10} | {:<15}".format(
            curr_dist, str(col), ref, obj_dist, status_text
        ))

        if Button.CENTER in ev3.buttons.pressed(): break
        wait(10)

finally:
    shutdown()