#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================
SPEED = 150  # Slow speed for precise adjustment

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

# Motor B is the Arm Lift
arm_lift = Motor(Port.B)

# =============================================================================
# 🎮 MAIN CONTROL LOOP
# =============================================================================

ev3.speaker.say("Manual Control")
print("--- CONTROLS ---")
print("UP BTN   = Move Arm UP")
print("DOWN BTN = Move Arm DOWN")
print("CENTER   = Save Zero & Exit")

ev3.light.on(Color.ORANGE)

while True:
    # Check which buttons are pressed
    pressed = ev3.buttons.pressed()

    # 1. MOVE UP
    if Button.UP in pressed:
        # Negative speed usually means "Up" for this build
        arm_lift.run(-SPEED) 
        
    # 2. MOVE DOWN
    elif Button.DOWN in pressed:
        arm_lift.run(SPEED)
        
    # 3. SAVE AND EXIT
    elif Button.CENTER in pressed:
        # Stop the motor first
        arm_lift.stop()
        wait(500)
        
        # MAGIC LINE: This tells the robot "HERE is 0"
        arm_lift.reset_angle(0)
        
        ev3.speaker.say("Zero Saved")
        print("New Zero Position Saved!")
        ev3.light.on(Color.GREEN)
        wait(2000)
        break # Exit the loop
        
    # 4. STOP (If no buttons pressed)
    else:
        arm_lift.hold() # Holds position so it doesn't fall

    wait(10) # Small delay to save CPU