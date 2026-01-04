#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================
SPEED = 150         # Speed for manual adjustment
Motor_Port = Port.B # Change if your arm is on a different port

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)
arm_lift = Motor(Motor_Port)

# =============================================================================
# 🛠️ CALIBRATION LOOP
# =============================================================================

def manual_adjust(step_name):
    """
    Lets you move the motor with buttons until you press Center.
    Returns the final angle.
    """
    ev3.speaker.say("Set " + step_name)
    print("--- SETTING: " + step_name + " ---")
    print("UP/DOWN: Move Arm")
    print("CENTER:  Confirm")
    
    while True:
        pressed = ev3.buttons.pressed()

        # 1. MOVE UP
        if Button.UP in pressed:
            arm_lift.run(-SPEED) # Negative usually moves UP
        
        # 2. MOVE DOWN
        elif Button.DOWN in pressed:
            arm_lift.run(SPEED)  # Positive usually moves DOWN
            
        # 3. CONFIRM (Center Button)
        elif Button.CENTER in pressed:
            arm_lift.stop()
            ev3.speaker.beep()
            wait(500) # Debounce
            break
            
        # 4. HOLD (If nothing pressed)
        else:
            arm_lift.hold()
            
        wait(10)
    
    return arm_lift.angle()

# --- MAIN PROGRAM ---

ev3.light.on(Color.ORANGE)

# STEP 1: SET THE "UP" (ZERO) POSITION
print("1. Move arm to TOP position.")
manual_adjust("Up")

# Reset the sensor so this exact spot is now "0"
arm_lift.reset_angle(0)
ev3.speaker.say("Zero Set")
print(">>> ZERO POINT SET! <<<")
print("Current Angle: 0")
wait(1000)

# STEP 2: SET THE "DOWN" POSITION
print("2. Move arm to BOTTOM position.")
down_angle = manual_adjust("Down")

# STEP 3: RESULT
ev3.light.on(Color.GREEN)
ev3.speaker.say("Calibration Complete")

print("\n" + "="*30)
print("   YOUR 'DOWN' NUMBER IS:")
print("      " + str(down_angle))
print("="*30 + "\n")

# Keep the number on screen for 10 seconds so you can write it down
wait(10000)