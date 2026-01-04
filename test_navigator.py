#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, ColorSensor, UltrasonicSensor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ 1. DRIVE SETTINGS
# =============================================================================
THRESHOLD = 45       
DRIVE_SPEED = 100    
TURN_GAIN = -1.2     

# =============================================================================
# ⚙️ 2. STATION CALIBRATION (From readings.txt)
# =============================================================================
# GREEN: Reads as Blue (19-21) or Green (5-12). Glints are Blue < 17.
MIN_GREEN_BLUE = 18

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options(speed=80, pitch=60)

left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
# Arm/Clamp motors defined but NOT used in init/shutdown
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

line_sensor = ColorSensor(Port.S3)
obstacle_sensor = UltrasonicSensor(Port.S1) # Added if you want to test obstacle detection too

robot = DriveBase(left_motor, right_motor, wheel_diameter=56, axle_track=114)

# =============================================================================
# 🛠️ SYSTEM FUNCTIONS (Clean Version)
# =============================================================================

def initialize():
    """Runs ONCE at the start. (No Arm/Clamp movement)"""
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    
    # --- NO ARM/CLAMP MOVEMENT HERE ---
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Line Follower Ready")
    wait(1000)

def shutdown():
    """Runs AUTOMATICALLY when Center Button is pressed. (No Arm/Clamp movement)"""
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutting down")
    
    # --- NO ARM/CLAMP MOVEMENT HERE ---
    
    # Release drive motors
    left_motor.stop()
    right_motor.stop()
    
    ev3.speaker.beep()

def check_station(target_id, color, reflection):
    # 1 = GREEN STATION
    if target_id == 1:
        if color == Color.GREEN: return True
        if color == Color.BLUE and reflection >= MIN_GREEN_BLUE: return True
    
    # 2 = YELLOW STATION
    elif target_id == 2:
        if color == Color.YELLOW or color == Color.BROWN: return True
        if color == Color.BLUE and reflection > 90: return True

    # 3 = ORANGE STATION
    elif target_id == 3:
        if color == Color.RED: return True
        
    return False

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    # Sequence: 1=Green, 2=Yellow, 3=Orange
    next_station = 1 

    # BLIND DRIVE SETTINGS (From your map info)
    # Start->Green is long. Green->Yellow=29cm. Yellow->Orange=37cm.
    blind_distance_mm = 200 # Initial safety buffer
    robot.reset()
    
    while True:
        # 1. SAFETY EXIT
        if Button.CENTER in ev3.buttons.pressed():
            break 
            
        col = line_sensor.color()
        ref = line_sensor.reflection()
        current_dist = robot.distance()
        
        # 2. BLIND DRIVE (Safety Zone)
        if current_dist < blind_distance_mm:
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
            continue
            
        # 3. STATION HUNTING
        if check_station(next_station, col, ref):
            robot.stop()
            
            # Announce
            if next_station == 1: 
                ev3.speaker.say("Green")
                next_station = 2
                blind_distance_mm = 150 # Ignore first 15cm (Green -> Yellow)
                
            elif next_station == 2: 
                ev3.speaker.say("Yellow")
                next_station = 3
                blind_distance_mm = 200 # Ignore first 20cm (Yellow -> Orange)
                
            elif next_station == 3: 
                ev3.speaker.say("Orange")
                next_station = 1
                blind_distance_mm = 150 # Ignore first 15cm (Orange -> Start)
            
            # Drive forward slightly to clear the patch
            robot.straight(100)
            robot.reset() 
            
        else:
            # 4. NORMAL DRIVING
            robot.drive(DRIVE_SPEED, (ref - THRESHOLD) * TURN_GAIN)
        
        wait(10)

finally:
    shutdown()