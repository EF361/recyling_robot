#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================

# 1. ARM SETTINGS (User Defined)
# "Up" for traveling/holding (-202)
ARM_UP_POS = -202     
# "Down" for picking up (5)
ARM_DOWN_POS = 5      
# Safe position for initialization
ARM_SAFE_POS = -202   
ARM_SPEED = 200

# 2. CLAMP SETTINGS
CLAMP_SPEED = 200
CLAMP_FORCE = 40      

# 3. LINE FOLLOWING
THRESHOLD = 45       
DRIVE_SPEED = 50     
TURN_GAIN = -1.2     

# 4. SCORE SYSTEM (Station Detection)
TRIGGER_SCORE = 6
MAX_SCORE = 10 

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2) 
line_sensor = ColorSensor(Port.S3)  

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🛠️ HELPER FUNCTIONS
# =============================================================================

def initialize():
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    
    # --- Arm Init ---
    # Move gently to find hard stop (if any), then reset
    # Assuming positive moves down/forward, we stall then pull back
    arm_lift.run_until_stalled(-202, then=Stop.COAST, duty_limit=40)
    arm_lift.reset_angle(0) # 0 is likely the bottom/stall point
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS) # Lift to safe
    
    # --- Clamp Init ---
    clamp.run_until_stalled(200, then=Stop.COAST, duty_limit=40)
    clamp.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Ready")
    wait(1000)

def shutdown():
    robot.stop()
    ev3.light.on(Color.RED)
    ev3.speaker.say("Shutting down")
    
    # Lower Arm
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    # Close Clamp
    clamp.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    
    ev3.speaker.beep()

def update_score(current_score, is_detected):
    if is_detected:
        return min(current_score + 2, MAX_SCORE)
    else:
        return max(current_score - 2, 0)

def identify_trash_color():
    """Checks color inside the claw."""
    c = clamp_sensor.color()
    # Basic logic - adjust if needed
    if c == Color.GREEN or c == Color.BLUE: return 1 
    if c == Color.YELLOW: return 2                   
    if c == Color.RED: return 3                      
    return 3 # Default to Metal

def pick_up_routine():
    robot.stop()
    ev3.speaker.say("Trash detected")
    
    # 1. Open Clamp
    clamp.run_target(CLAMP_SPEED, 90) 
    
    # 2. Lower Arm (To User Defined Position 5)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    
    # 3. Grab
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=60)
    
    # 4. Lift Arm (To User Defined Position -202)
    arm_lift.run_target(ARM_SPEED, ARM_UP_POS)
    
    # 5. Identify
    item_id = identify_trash_color()
    if item_id == 1: ev3.speaker.say("Plastic")
    elif item_id == 2: ev3.speaker.say("Paper")
    elif item_id == 3: ev3.speaker.say("Metal")
    
    return item_id

def deliver_routine():
    robot.stop()
    ev3.speaker.say("Dropping")
    
    # Turn to bin
    robot.turn(90)
    robot.straight(200) 
    
    # Drop
    clamp.run_target(CLAMP_SPEED, 90) 
    wait(500)
    
    # Return
    robot.straight(-200)
    robot.turn(-90)
    
    # Close Clamp & Resume
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=40)

def check_station_fingerprints(color, reflection):
    """
    Returns: 1=Green, 2=Yellow, 3=Orange, 0=None
    Based on 'line_detection.txt' calibration.
    """
    # 1. GREEN
    if color == Color.GREEN: return 1
    if color == Color.BLUE and (18 <= reflection <= 29): return 1
        
    # 2. YELLOW
    if color == Color.YELLOW or color == Color.BROWN: return 2
    if color == Color.BLUE and (30 <= reflection <= 70): return 2

    # 3. ORANGE
    if color == Color.RED: return 3
    if color == Color.BLUE and (reflection > 90): return 3
        
    return 0

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    # State Variables
    has_item = False
    carried_item_id = 0 
    
    # Sequence: 1=Green, 2=Yellow, 3=Orange
    target_station = 1 
    ev3.speaker.say("Hunting Green")
    
    score = 0
    cooldown_timer = 0
    
    while True:
        if Button.CENTER in ev3.buttons.pressed(): break
        
        col = line_sensor.color()
        ref = line_sensor.reflection()
        dist = obstacle_sensor.distance()
        
        # --- A. TRASH PICKUP (Highest Priority) ---
        if (not has_item) and (dist < 50):
            carried_item_id = pick_up_routine()
            has_item = True
            # Resume loop fresh to reset sensors
            continue 

        # --- B. COOLDOWN ---
        if cooldown_timer > 0:
            cooldown_timer -= 1
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            wait(10)
            continue

        # --- C. STATION DETECTION (Sequence Mode) ---
        detected_id = check_station_fingerprints(col, ref)
        
        # "Stand By" Logic: Only look for the Target Station
        if detected_id == target_station:
            score = update_score(score, True)
        else:
            # If we see the wrong station (or nothing), score decays
            score = update_score(score, False)
            
        # --- D. STATION FOUND ---
        if score >= TRIGGER_SCORE:
            robot.stop()
            
            # 1. Announce Station
            if target_station == 1:
                ev3.speaker.say("Green Station")
                print(">>> Found Green")
                next_target = 2
            elif target_station == 2:
                ev3.speaker.say("Yellow Station")
                print(">>> Found Yellow")
                next_target = 3
            elif target_station == 3:
                ev3.speaker.say("Orange Station")
                print(">>> Found Orange")
                next_target = 1
            
            # 2. Drop Item? (Only if correct match)
            if has_item and (carried_item_id == target_station):
                ev3.speaker.say("Correct")
                deliver_routine()
                has_item = False
                carried_item_id = 0
            
            # 3. Switch Target Logic
            target_station = next_target
            
            # 4. Reset & Cooldown
            score = 0
            cooldown_timer = 200 # 2 Seconds
            
            # No forward dash -> Robot resumes line following in next loop
            
        else:
            # --- E. LINE FOLLOWER ---
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            
        wait(10)

finally:
    shutdown()