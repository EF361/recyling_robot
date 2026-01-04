#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS
# =============================================================================

# 1. Line Following
BLACK_VAL = 7
WHITE_VAL = 80
THRESHOLD = 43       
DRIVE_SPEED = 50     
TURN_GAIN = -1.2     

# 2. Station Confidence Settings (The Fix)
# Instead of "5 in a row", we need a Score of 20.
# +2 for match, -1 for miss. 
# This filters short glints but catches messy stations.
TRIGGER_SCORE = 20
MAX_SCORE = 30 # Cap the score so it doesn't grow forever

# 3. Fingerprints
# GREEN: Blue/Green color. Refl < 23 (Opened slightly to catch deep green)
GREEN_MAX_REFL = 23 

# 4. Arm & Clamp
ARM_SPEED = 200
ARM_UP_POS = 0       
ARM_DOWN_POS = 5     
ARM_SAFE_POS = -202  
CLAMP_SPEED = 200
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
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    
    # Clamp Init
    clamp.run_until_stalled(CLAMP_SPEED, then=Stop.COAST, duty_limit=CLAMP_FORCE)
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    clamp.reset_angle(0)
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Confidence System Ready")
    wait(1000)

def shutdown():
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutting down")
    
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_until_stalled(-CLAMP_SPEED, then=Stop.HOLD, duty_limit=CLAMP_FORCE)
    
    left_motor.stop()
    right_motor.stop()
    arm_lift.stop()
    clamp.stop()
    ev3.speaker.beep()

# =============================================================================
# 🧠 SMART SCORING SYSTEM
# =============================================================================

def update_score(current_score, is_detected):
    """
    Increases score if detected (+2), decreases if not (-1).
    Keeps score between 0 and MAX_SCORE.
    """
    if is_detected:
        return min(current_score + 2, MAX_SCORE)
    else:
        return max(current_score - 1, 0)

def check_station_fingerprints(color, reflection):
    """
    Returns 0 (None), 1 (Green), 2 (Yellow), 3 (Orange)
    """
    # GREEN CHECK (Blue/Green + Darker than 23)
    # We allow slightly higher reflection because the Score System handles the noise.
    if (color == Color.GREEN or color == Color.BLUE) and (reflection <= GREEN_MAX_REFL):
        return 1
        
    # YELLOW CHECK (Yellow Color)
    if color == Color.YELLOW:
        return 2

    # ORANGE CHECK (Red Color)
    if color == Color.RED:
        return 3
        
    return 0

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    # Confidence Scores (Start at 0)
    score_green = 0
    score_yellow = 0
    score_orange = 0
    
    cooldown_timer = 0 
    
    while True:
        # 1. Safety Exit
        if Button.CENTER in ev3.buttons.pressed():
            break 
            
        # 2. READ SENSORS
        col = line_sensor.color()
        ref = line_sensor.reflection()
        
        # 3. CHECK COOLDOWN 
        if cooldown_timer > 0:
            cooldown_timer -= 1
            deviation = ref - THRESHOLD
            turn_rate = deviation * TURN_GAIN
            robot.drive(DRIVE_SPEED, turn_rate)
            wait(10)
            continue 

        # 4. IDENTIFY RAW SIGNAL
        # What does the sensor "think" it sees right now?
        raw_id = check_station_fingerprints(col, ref)
        
        # 5. UPDATE SCORES (The Magic Part)
        # If raw_id is 1 (Green), score_green goes up, others go down.
        score_green  = update_score(score_green,  raw_id == 1)
        score_yellow = update_score(score_yellow, raw_id == 2)
        score_orange = update_score(score_orange, raw_id == 3)
        
        # (Optional Debug: Uncomment to see scores in terminal)
        # print(score_green, score_yellow, score_orange)

        # 6. CHECK TRIGGERS
        detected_station = 0
        
        if score_green >= TRIGGER_SCORE:
            detected_station = 1
            station_name = "Green Station"
        elif score_yellow >= TRIGGER_SCORE:
            detected_station = 2
            station_name = "Yellow Station"
        elif score_orange >= TRIGGER_SCORE:
            detected_station = 3
            station_name = "Orange Station"

        # 7. EXECUTE
        if detected_station > 0:
            robot.stop()
            ev3.speaker.say(station_name)
            
            # Reset ALL scores
            score_green = 0
            score_yellow = 0
            score_orange = 0
            
            # Cooldown
            cooldown_timer = 300 
            
        else:
            # Line Follower
            deviation = ref - THRESHOLD
            turn_rate = deviation * TURN_GAIN
            robot.drive(DRIVE_SPEED, turn_rate)
        
        wait(10)

finally:
    shutdown()