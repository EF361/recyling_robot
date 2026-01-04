#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ 1. CALIBRATED SENSORS (From your readings.txt & info.txt)
# =============================================================================

# LINE TRACKING
# Black is ~6-12[cite: 1444]. White is ~50-90[cite: 169].
THRESHOLD = 45       
DRIVE_SPEED = 100    # Fast enough for demo, slow enough for grip
TURN_GAIN = -1.2     # Follow Right Edge of black line

# STATION RECOGNITION (From readings.txt)
# GREEN: Reads as Blue (19-21) or Green (5-12). Glints are Blue < 17.
# Rule: Green OR (Blue > 18)
MIN_GREEN_BLUE = 18

# YELLOW: Reads as Blue (100) or Yellow/Brown.
# Rule: Yellow OR Brown OR (Blue > 95)

# ORANGE: Reads as Red (95-100).
# Rule: Red

# TRASH ID (From info.txt) 
# Plastic Bottle: Refl 8-10 (Dark)
# Alum Scrub: Refl 10-12 (Dark)
# Paper: Refl 46-48 (Bright)
# Yellow Plastic: Refl 60-80 (Very Bright)

# MECHANISM
ARM_UP_POS = -202     
ARM_DOWN_POS = 5      
ARM_SPEED = 200
CLAMP_SPEED = 200

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
    ev3.speaker.say("Golden Demo")
    
    # Reset Arm
    arm_lift.run_until_stalled(200, then=Stop.COAST, duty_limit=40)
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_UP_POS) 
    
    # Reset Clamp
    clamp.run_until_stalled(200, then=Stop.COAST, duty_limit=40)
    clamp.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    
    ev3.light.on(Color.GREEN)
    wait(500)

def shutdown():
    robot.stop()
    ev3.light.on(Color.RED)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(-200, then=Stop.HOLD, duty_limit=40)
    ev3.speaker.beep()

def identify_trash_item():
    """
    Identifies your 4 specific items based on Refl/Color 
    Returns: 1=Plastic, 2=Paper, 3=Metal
    """
    col = clamp_sensor.color()
    ref = clamp_sensor.reflection()
    
    # 1. Yellow Plastic (Refl 60-80) -> PLASTIC (Green Station)
    if ref > 55: 
        return 1 
    
    # 2. White Paper (Refl 46-48) -> PAPER (Yellow Station)
    if 40 <= ref <= 55:
        return 2
        
    # 3. Alum Scrub (Refl 10-12) -> METAL (Orange Station)
    if col == Color.BLACK or (8 <= ref <= 15):
        # Tie-breaker between Bottle and Scrub?
        # Usually Scrub is slightly shinier or has color noise.
        # For now, map both low-reflection items to their bins.
        # If scrub is Metal:
        return 3
        
    # 4. Plastic Bottle (Refl 8-10) -> PLASTIC (Green Station)
    # This overlaps with Scrub. If you need to separate them:
    # Bottle might be distinctly Color.BLACK while Scrub reflects weirdly.
    # defaulting to Plastic if unsure
    return 1 

def pick_up_routine():
    robot.stop()
    ev3.speaker.say("Trash")
    
    clamp.run_target(CLAMP_SPEED, 90) 
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=60)
    arm_lift.run_target(ARM_SPEED, ARM_UP_POS)
    
    item_type = identify_trash_item()
    
    if item_type == 1: ev3.speaker.say("Plastic")
    elif item_type == 2: ev3.speaker.say("Paper")
    elif item_type == 3: ev3.speaker.say("Metal")
    
    return item_type

def drop_routine():
    robot.stop()
    ev3.speaker.say("Dropping")
    robot.turn(90)
    robot.straight(150) 
    clamp.run_target(CLAMP_SPEED, 90) 
    wait(500)
    robot.straight(-150)
    robot.turn(-90)
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=40)

def check_station(target_id, color, reflection):
    """
    Checks ONLY for the specific station we expect next.
    """
    # 1 = GREEN STATION
    if target_id == 1:
        # Green OR Bright Blue (Anti-Glint logic)
        if color == Color.GREEN: return True
        if color == Color.BLUE and reflection >= MIN_GREEN_BLUE: return True
    
    # 2 = YELLOW STATION
    elif target_id == 2:
        # Yellow, Brown, or Maxed Blue
        if color == Color.YELLOW or color == Color.BROWN: return True
        if color == Color.BLUE and reflection > 90: return True

    # 3 = ORANGE STATION
    elif target_id == 3:
        # Red
        if color == Color.RED: return True
        
    return False

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    has_item = False
    carried_item = 0 
    
    # MAP LOGIC:
    # 1 = Green, 2 = Yellow, 3 = Orange
    next_station = 1 
    
    # BLIND DRIVE DISTANCE (Safety Buffer)
    # When we leave a station/start, we ignore lines for this many mm.
    # Start -> Green is HUGE (200cm+).
    # Green -> Yellow is 29cm.
    # Yellow -> Orange is 37cm.
    blind_distance_mm = 200 # Initial drive from Start Corner
    
    # Reset distance counter
    robot.reset()
    
    while True:
        if Button.CENTER in ev3.buttons.pressed(): break
        
        # 1. READ SENSORS
        col = line_sensor.color()
        ref = line_sensor.reflection()
        dist = obstacle_sensor.distance()
        current_dist = robot.distance()
        
        # 2. BLIND DRIVE CHECK
        # If we haven't driven far enough from the last point, IGNORE STATIONS.
        if current_dist < blind_distance_mm:
            # Just follow line, ignore station colors
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            
            # TRASH CHECK is allowed during blind drive? 
            # Yes, trash might be anywhere.
            if (not has_item) and (dist < 50):
                carried_item = pick_up_routine()
                has_item = True
                # Reset robot distance so we don't mess up the blind calculation?
                # Actually, no. Picking up shouldn't reset our map progress.
                
            continue
            
        # 3. STATION HUNTING
        # We are past the blind zone, now look for the SPECIFIC next station.
        if check_station(next_station, col, ref):
            robot.stop()
            
            # A. Announce
            if next_station == 1: ev3.speaker.say("Green")
            elif next_station == 2: ev3.speaker.say("Yellow")
            elif next_station == 3: ev3.speaker.say("Orange")
            
            # B. Drop if match
            if has_item and (carried_item == next_station):
                ev3.speaker.say("Correct")
                drop_routine()
                has_item = False
                carried_item = 0
            
            # C. Update Map & Set Blind Distance
            if next_station == 1: 
                # Leaving Green -> Going Yellow (29cm away)
                next_station = 2
                blind_distance_mm = 150 # Ignore for 15cm
                
            elif next_station == 2:
                # Leaving Yellow -> Going Orange (37cm away)
                next_station = 3
                blind_distance_mm = 200 # Ignore for 20cm
                
            elif next_station == 3:
                # Leaving Orange -> Going Start/Green (Long way)
                next_station = 1
                blind_distance_mm = 150 # Clear the orange patch
                
            # Drive forward a bit to clear the patch
            robot.straight(100)
            robot.reset() # Reset distance to 0 for the new blind segment
            
        else:
            # 4. NORMAL LINE FOLLOWING
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            
            # Trash Check
            if (not has_item) and (dist < 50):
                carried_item = pick_up_routine()
                has_item = True

        wait(10)

finally:
    shutdown()