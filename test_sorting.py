#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait

# =============================================================================
# ⚙️ SETTINGS (Same as Main)
# =============================================================================
ARM_SPEED = 200
ARM_UP_POS = 0       
ARM_DOWN_POS = 5   # ⚠️ Adjust if your arm hits the floor!
CLAMP_SPEED = 200
CLAMP_FORCE = 60     # Slightly higher force to ensure grip

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2) # The sensor INSIDE the claw

# =============================================================================
# 🛠️ HELPER FUNCTIONS
# =============================================================================

def initialize():
    ev3.light.on(Color.ORANGE)
    print("Init: Resetting Arm...")
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, -200) # Move up to safe pos
    
    print("Init: Calibrating Clamp...")
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.COAST, duty_limit=50) # Open
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=50) # Close
    clamp.reset_angle(0)
    
    ev3.speaker.say("Sorting Test Ready")
    print(">>> Put object in front of sensor <<<")


def identify_trash():
    """Reads color inside the closed claw"""
    c = clamp_sensor.color()
    r = clamp_sensor.reflection()
    
    print("Seen: " + str(c) + " | Refl: " + str(r))
    
    # ⚠️ CALIBRATION ZONE:
    # If it guesses wrong, check the printed Color/Refl numbers here!
    
    if c == Color.GREEN or c == Color.BLUE: return "Plastic"
    if c == Color.WHITE: return "Paper"
    if c == Color.RED: return "Metal"
    if c == Color.WHITE: return "Unknown"
    
    return "Metal" # Default fallback

# =============================================================================
# 🚀 TEST LOOP
# =============================================================================

initialize()

while True:
    # 1. Exit Button
    if Button.CENTER in ev3.buttons.pressed(): break
    
    # 2. Check Distance
    dist = obstacle_sensor.distance()
    
    if dist < 50: # If object is closer than 50mm
        ev3.speaker.beep()
        
        # A. OPEN
        clamp.run_target(CLAMP_SPEED, 90) # Open wide
        
        # B. LOWER
        arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
        
        # C. WAIT FOR YOU TO PLACE IT
        wait(1000) 
        
        # D. GRAB
        clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
        
        # E. LIFT
        arm_lift.run_target(ARM_SPEED, 0)
        wait(500)
        
        # F. IDENTIFY
        material = identify_trash()
        ev3.speaker.say(material)
        print("Identified: " + material)
        
        wait(1000)
        
        # G. RELEASE (So you can test the next one)
        ev3.speaker.say("Releasing")
        clamp.run_target(CLAMP_SPEED, 90)
        wait(1000)
        
        # H. RESET
        # Close clamp slightly and go back to safe height
        clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=50)
        arm_lift.run_target(ARM_SPEED, -200)
        
        print(">>> Ready for next item <<<")
        
    wait(100)