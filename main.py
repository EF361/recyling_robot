#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait, Stopwatch  # Added Stopwatch
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ 1. GLOBAL SETTINGS
# =============================================================================
THRESHOLD = 44       
DRIVE_SPEED = 50    
TURN_GAIN = -1.2     

# Corner Logic
WHITE_THRESHOLD = 75 
VALID_WHITE_DIST = 50   
CORNER_COOLDOWN = 200   

# Arm/Clamp
ARM_SPEED = 200
ARM_SAFE_POS = -250
ARM_DOWN_POS = 0
CLAMP_SPEED = 200
CLAMP_FORCE = 70
CLAMP_OPEN_ANGLE = -75

# Station
MIN_GREEN_REFL = 18
MAX_GREEN_REFL = 30 

# =============================================================================
# 🔌 2. SETUP
# =============================================================================
ev3 = EV3Brick()
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
line_sensor = ColorSensor(Port.S3)   
clamp_sensor = ColorSensor(Port.S2)  
obstacle_sensor = UltrasonicSensor(Port.S1) 
robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 📊 3. TRASH DATABASE
# =============================================================================
TRASH_DB = [
    ("None",    0, 5,   [None, Color.BLACK]),
    ("Plastic", 6, 20,  [Color.BLACK, Color.BROWN]),
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

# =============================================================================
# 🛠️ 4. CORE FUNCTIONS
# =============================================================================

def initialize():
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
    ev3.speaker.say("Object detected")
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

def check_station(target_id, color, reflection):
    if target_id == 1: # Green (Reads as Blue)
        return color == Color.BLUE and MIN_GREEN_REFL <= reflection <= MAX_GREEN_REFL
    elif target_id == 2: # Yellow
        return color in [Color.YELLOW, Color.BROWN] or (color == Color.BLUE and reflection > 90)
    elif target_id == 3: # Orange
        return color == Color.RED
    return False

# =============================================================================
# 🚀 5. MAIN MISSION LOOP
# =============================================================================
try:
    initialize()
    
    # Start the timer immediately after initialization
    mission_timer = Stopwatch()
    
    next_station = 1
    corners_passed = 0
    white_start_dist = -1
    last_corner_finish_dist = -200
    blind_distance_mm = 1500 
    
    while True:
        if Button.CENTER in ev3.buttons.pressed(): break
        
        col, ref = line_sensor.color(), line_sensor.reflection()
        obj_dist = obstacle_sensor.distance()
        curr_dist = robot.distance()
        turn_rate = (ref - THRESHOLD) * TURN_GAIN
        
        # --- 1. TRASH DETECTION ---
        if obj_dist < 50:
            pick_and_drop()
            robot.reset() 

        # --- 2. CONTINUOUS WHITE CORNER COUNTING ---
        # ⚠️ MODIFIED: Only count if more than 5000ms (5s) have passed
        if mission_timer.time() > 5000:
            if next_station == 1 and (curr_dist - last_corner_finish_dist > CORNER_COOLDOWN):
                if ref > WHITE_THRESHOLD:
                    if white_start_dist == -1:
                        white_start_dist = curr_dist 
                    
                    if (curr_dist - white_start_dist) >= VALID_WHITE_DIST:
                        corners_passed += 1
                        ev3.speaker.beep()
                        print("Corner confirmed: " + str(corners_passed))
                        last_corner_finish_dist = curr_dist
                        white_start_dist = -1 
                else:
                    white_start_dist = -1 

        # --- 3. NAVIGATION ---
        if curr_dist < blind_distance_mm:
            robot.drive(DRIVE_SPEED, turn_rate)
            continue
            
        can_hunt = (next_station == 1 and corners_passed >= 3) or (next_station > 1)
        
        if can_hunt and check_station(next_station, col, ref):
            robot.stop()
            ev3.speaker.say("Station")
            
            if next_station == 1: 
                next_station = 2
                blind_distance_mm = 200 
            elif next_station == 2: 
                next_station = 3
                blind_distance_mm = 250 
            elif next_station == 3: 
                next_station = 1
                blind_distance_mm = 1500 
                corners_passed = 0
                last_corner_finish_dist = curr_dist
                # Optional: mission_timer.reset() if you want the 5s delay every lap
            
            robot.straight(60) 
            robot.reset()
        else:
            robot.drive(DRIVE_SPEED, turn_rate)
        
        wait(10)

finally:
    shutdown()