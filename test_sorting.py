#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================
ARM_SPEED = 200
ARM_SAFE_POS = -250    # UP / SAFE
ARM_DOWN_POS = 0       # DOWN / FLOOR

# CLAMP SETTINGS
CLAMP_SPEED = 200
CLAMP_FORCE = 70       # Force 70
CLAMP_OPEN_ANGLE = -75 # Angle -75

# =============================================================================
# 📊 TRASH ID CONFIGURATION (THE LIST)
# =============================================================================
# Format: ("Material Name", Min_Ref, Max_Ref, [List_of_Valid_Colors])

TRASH_DB = [
    # 1. Nothing / Empty (Low Ref + None/Black)
    ("None",    0, 5,   [None, Color.BLACK]),
    
    # 2. Water Bottle (Dark + Black/Brown)
    ("Plastic", 6, 20,  [Color.BLACK, Color.BROWN]),
    
    # 3. Paper (Bright + White/Blue)
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

arm_lift = Motor(Port.B)
clamp = Motor(Port.A)
obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2) 

# =============================================================================
# 🛠️ HELPER FUNCTIONS
# =============================================================================

def wait_with_check(duration_ms):
    loops = int(duration_ms / 50)
    for _ in range(loops):
        if Button.CENTER in ev3.buttons.pressed():
            return False 
        wait(50)
    return True

def identify_trash_item():
    """
    Scans 5 times. Checks Reflection AND Color.
    Returns the LAST valid match found.
    """
    final_decision = "None" # Default
    
    for i in range(5):
        # 1. Capture readings
        col = clamp_sensor.color()
        ref = clamp_sensor.reflection()
        amb = clamp_sensor.ambient()
        
        # 2. Print Debug Log
        print("\n[OBJECT DETECTED - SAMPLE " + str(i+1) + "/5]")
        print("-------------------------")
        print("Color      : " + str(col))
        print("Reflection : " + str(ref) + "%")
        print("Ambient    : " + str(amb) + "%")
        print("-------------------------")
        
        # 3. Decision Logic (Ref + Color)
        match_found = False
        
        for item in TRASH_DB:
            name, min_ref, max_ref, valid_colors = item
            
            # CHECK 1: Reflection Range
            if min_ref <= ref <= max_ref:
                # CHECK 2: Color Match
                if col in valid_colors:
                    final_decision = name
                    match_found = True
                    print(">> Match Found: " + name)
        
        if not match_found:
             print(">> No Match (Unknown Item)")
        
        wait(200)
    
    print(">> FINAL DECISION: " + final_decision + "\n")
    return final_decision

def pick_up_sequence():
    """
    Lifts and Identifies.
    Returns: item_name (String)
    """
    ev3.speaker.say("Trash detected")
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    
    item_name = identify_trash_item()
    ev3.speaker.say(item_name)
    
    # Only say "Holding" if it's NOT empty
    if item_name != "None":
        ev3.speaker.say("Holding")
        
    return item_name

def drop_sequence():
    ev3.speaker.say("Dropping")
    clamp.run_target(CLAMP_SPEED, CLAMP_OPEN_ANGLE)
    wait(1000)
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)

# =============================================================================
# INITIALIZE
# =============================================================================
def initialize():
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("Initialize")

    # 1️⃣ ARM (Quiet Mode)
    arm_lift.reset_angle(0)
    ev3.speaker.say("Lifting Arm")
    # Use BRAKE instead of HOLD to stop buzzing
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS, then=Stop.BRAKE)
    wait(300)

    # 2️⃣ CLAMP (Quiet Mode)
    ev3.speaker.say("Calibrating Clamp")
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.COAST, duty_limit=40)
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=40)
    clamp.reset_angle(0)
    # Release tension slightly (5 degrees) to stop buzzing
    clamp.run_target(CLAMP_SPEED, -5, then=Stop.COAST)

    ev3.light.on(Color.YELLOW)
    ev3.speaker.say("Press center to start")

    while Button.CENTER not in ev3.buttons.pressed():
        wait(20)
    while Button.CENTER in ev3.buttons.pressed():
        wait(20) 
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Scanning")

# =============================================================================
# SHUTDOWN
# =============================================================================
def shutdown():
    ev3.light.on(Color.RED)
    ev3.speaker.say("Shutdown")
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    wait(300)
    ev3.speaker.beep()

# =============================================================================
# MAIN LOOP
# =============================================================================
initialize()

try:
    while True:
        if Button.CENTER in ev3.buttons.pressed():
            break

        dist = obstacle_sensor.distance()
        if dist < 50:
            
            # A. PICK UP & IDENTIFY
            detected_item = pick_up_sequence()
            
            # ⚠️ LOGIC CHANGE: If "None", Skip Wait/Drop
            if detected_item == "None":
                # Just wait a bit and go back to scanning
                wait(1000) 
                continue 
            
            # B. SMART WAIT (Only for Real Items)
            ev3.light.on(Color.YELLOW)
            if not wait_with_check(5000): break 
            ev3.light.on(Color.GREEN)
            
            # C. DROP (Only for Real Items)
            drop_sequence()
            
            wait(1000)

        wait(10)

finally:
    shutdown()