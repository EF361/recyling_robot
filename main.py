#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================

# LINE FOLLOWING
# Based on your data: Black(~8), White(~90-100). Threshold 45 is solid.
THRESHOLD = 45       
DRIVE_SPEED = 50     
TURN_GAIN = -1.2     

# SCORE SYSTEM
# Trigger fast (3 readings)
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
    ev3.speaker.say("Sequence Mode")
    
    # Arm Reset
    arm_lift.run_until_stalled(200, then=Stop.COAST, duty_limit=40)
    arm_lift.reset_angle(0)
    arm_lift.run_target(200, -202) 
    
    # Clamp Reset
    clamp.run_until_stalled(200, then=Stop.COAST, duty_limit=40)
    clamp.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Ready")
    wait(1000)

def shutdown():
    robot.stop()
    ev3.light.on(Color.RED)
    ev3.speaker.say("Shutting down")
    ev3.speaker.beep()

def update_score(current_score, is_detected):
    if is_detected:
        return min(current_score + 2, MAX_SCORE)
    else:
        return max(current_score - 2, 0)

def check_station_fingerprints(color, reflection):
    """
    Returns: 1=Green, 2=Yellow, 3=Orange, 0=None
    Based on 'line_detection.txt' analysis.
    """
    
    # 1. GREEN STATION
    # Signature: Color.GREEN (Refl ~14) OR Color.BLUE (Refl 20-29)
    # Glints are Blue < 18. We strictly exclude them.
    if color == Color.GREEN:
        return 1
    if color == Color.BLUE and (18 <= reflection <= 29):
        return 1
        
    # 2. YELLOW STATION
    # Signature: Color.YELLOW (Refl 27) OR Color.BLUE (Refl 30-70)
    if color == Color.YELLOW or color == Color.BROWN:
        return 2
    if color == Color.BLUE and (30 <= reflection <= 70):
        return 2

    # 3. ORANGE STATION
    # Signature: Color.RED (Refl 97) OR Color.BLUE (Refl > 90)
    if color == Color.RED:
        return 3
    if color == Color.BLUE and (reflection > 90):
        return 3
        
    return 0

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    # SEQUENCE LOGIC
    # 1 = Hunting Green
    # 2 = Hunting Yellow
    # 3 = Hunting Orange
    target_station = 1 
    ev3.speaker.say("Hunting Green")
    
    # Scores
    score = 0
    cooldown_timer = 0
    
    while True:
        if Button.CENTER in ev3.buttons.pressed(): break
        
        col = line_sensor.color()
        ref = line_sensor.reflection()
        
        # --- 1. COOLDOWN ---
        if cooldown_timer > 0:
            cooldown_timer -= 1
            # Just follow the line while cooling down
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            wait(10)
            continue

        # --- 2. IDENTIFY ---
        detected_id = check_station_fingerprints(col, ref)
        
        # --- 3. FILTER BY TARGET (The "Stand By" Logic) ---
        # Only increase score if we see the station we are looking for.
        if detected_id == target_station:
            score = update_score(score, True)
        else:
            score = update_score(score, False)
            
        # --- 4. TRIGGER ACTION ---
        if score >= TRIGGER_SCORE:
            robot.stop()
            
            # Announce & Switch Target
            if target_station == 1:
                ev3.speaker.say("Green Station")
                print(">>> FOUND GREEN. Next: Yellow")
                target_station = 2 # Stand by for Yellow
                
            elif target_station == 2:
                ev3.speaker.say("Yellow Station")
                print(">>> FOUND YELLOW. Next: Orange")
                target_station = 3 # Stand by for Orange
                
            elif target_station == 3:
                ev3.speaker.say("Orange Station")
                print(">>> FOUND ORANGE. Next: Green")
                target_station = 1 # Stand by for Green
            
            # Reset
            score = 0
            # 200 loops * 10ms = 2 seconds cooldown
            # This prevents re-triggering while on the same patch
            cooldown_timer = 200 
            
            # --- REMOVED THE DRIVE FORWARD DASH HERE ---
            # Robot will resume line following immediately in next loop
            
        else:
            # --- 5. LINE FOLLOWING ---
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            
        wait(10)

finally:
    shutdown()