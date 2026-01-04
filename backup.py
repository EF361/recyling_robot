#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS

# BACKUP FOR INITIALIZATION AND SHUTTING DOWN THE ROBOT WITH LINE FOLLOWER ONLY
# =============================================================================

# 1. Line Following
BLACK_VAL = 7
WHITE_VAL = 80
THRESHOLD = (BLACK_VAL + WHITE_VAL) / 2
DRIVE_SPEED = 50     
TURN_GAIN = -1.2     # Negative = Follow Right Edge

# 2. Arm Settings
ARM_SPEED = 200
ARM_UP_POS = 0       
ARM_DOWN_POS = 5     
ARM_SAFE_POS = -202  

# 3. Clamp Settings
CLAMP_SPEED = 200
# Limit force to 40% to prevent "Break" sound when hitting wall
CLAMP_FORCE = 40     

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options(speed=80, pitch=60)

left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2)
line_sensor = ColorSensor(Port.S3)

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🛠️ SYSTEM FUNCTIONS
# =============================================================================

def initialize():
    """Runs ONCE at the start."""
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    
    # --- 1. ARM INIT ---
    arm_lift.reset_angle(0)
    print("Init: Moving Arm to Safe Height...")
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    
    # --- 2. CLAMP CALIBRATION (The Fix) ---
    print("Init: Calibrating Clamp...")
    ev3.speaker.say("Calibrating Clamp")

    # Step A: Open gently until it hits the limit
    # Positive speed = Open. duty_limit=40 prevents loud clicking.
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.COAST, duty_limit=CLAMP_FORCE)
    
    # Step B: Close gently until it hits the limit
    # Negative speed = Close.
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    
    # Step C: Reset Angle so the robot knows "Here is Closed (0)"
    clamp.reset_angle(0)
    
    # (Optional) Open slightly to be ready? Or stay closed?
    # Staying closed is safer for driving.
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Line Follower Ready")
    wait(1000)

def shutdown():
    """Runs AUTOMATICALLY when Center Button is pressed."""
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutting down")
    
    # 1. Lower Arm safely
    print("Shutdown: Lowering Arm...")
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    
    # 2. Close Clamp Gently
    print("Shutdown: Closing Clamp...")
    # Using run_until_stalled ensures it closes tight but stops before "clicking"
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    
    # 3. Release motors
    left_motor.stop()
    right_motor.stop()
    arm_lift.stop()
    clamp.stop()
    
    ev3.speaker.beep()

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    while True:
        # 1. SAFETY EXIT
        if Button.CENTER in ev3.buttons.pressed():
            break 
            
        # 2. LINE FOLLOWER (Only)
        current_reflect = line_sensor.reflection()
        
        # Calculate Turn (-1.2 Gain for Right Edge logic)
        deviation = current_reflect - THRESHOLD
        turn_rate = deviation * TURN_GAIN
        
        robot.drive(DRIVE_SPEED, turn_rate)

finally:
    shutdown()