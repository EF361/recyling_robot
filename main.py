#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Port, Color, Button
from pybricks.tools import wait
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ SETTINGS (Your Final Values)
# =============================================================================

# 1. Arm Settings
ARM_SPEED = 200
ARM_UP_POS = 0       # "Carrying" height
ARM_DOWN_POS = 5     # "Grabbing" height (Floor level)
ARM_SAFE_POS = -202  # "Driving" height (Safe clearance)

# 2. Driving Settings
LINE_THRESHOLD = 43  # (Black 7 + White 80) / 2
DRIVE_SPEED = 50
TURN_GAIN = -1.2

# 3. Station Logic
GREEN_REFLECT_MAX = 30
YELLOW_REFLECT_MIN = 90

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)
ev3.speaker.set_speech_options(speed=80, pitch=60)

# Hardware
left_motor = Motor(Port.D)
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

# Sensors
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
    
    # Reset Arm Logic
    arm_lift.reset_angle(0)
    
    # Lift to SAFE Height
    print("Init: Moving Arm to Safe Height...")
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    
    # Close Clamp
    print("Init: Closing Clamp...")
    clamp.run_time(-ARM_SPEED, 1000) 
    
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Ready")
    wait(1000)

def shutdown():
    """Runs AUTOMATICALLY when Loop Ends."""
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutting down")
    
    # Lower Arm safely
    print("Shutdown: Lowering Arm...")
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    
    # Close Clamp
    clamp.run_time(-ARM_SPEED, 1000)
    
    # Release motors
    left_motor.stop()
    right_motor.stop()
    arm_lift.stop()
    clamp.stop()
    
    ev3.speaker.beep()

# =============================================================================
# 🧠 HELPER FUNCTIONS
# =============================================================================

def get_station_id(sensor):
    col = sensor.color()
    ref = sensor.reflection()
    
    if col == Color.RED: return 3 # Orange
    if (col == Color.BLUE or col == Color.YELLOW) and ref >= YELLOW_REFLECT_MIN: return 2 # Yellow
    if (col == Color.BLUE or col == Color.GREEN) and ref <= GREEN_REFLECT_MAX and ref > 12: return 1 # Green
    return 0

def pick_up_routine():
    robot.stop()
    ev3.speaker.say("Object detected")
    
    # Open -> Down -> Close -> Up
    clamp.run_time(ARM_SPEED, 1000)
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    clamp.run_time(-ARM_SPEED, 1000)       
    arm_lift.run_target(ARM_SPEED, ARM_UP_POS)
    
    wait(500)
    item_id = 0
    detected = clamp_sensor.color()
    
    if detected == Color.GREEN: item_id = 1; ev3.speaker.say("This is Plastic")
    elif detected == Color.YELLOW: item_id = 2; ev3.speaker.say("This is Paper")
    elif detected == Color.RED: item_id = 3; ev3.speaker.say("This is Metal")
    else: item_id = 3; ev3.speaker.say("Unknown")
        
    return item_id

def deliver_routine():
    robot.stop()
    ev3.speaker.say("Dropping item")
    
    robot.turn(90)
    robot.straight(300) 
    
    clamp.run_time(ARM_SPEED, 1000) # Open
    wait(500)
    
    robot.straight(-300)
    robot.turn(-90)
    
    clamp.run_time(-ARM_SPEED, 1000) # Close

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================

initialize() 

try:
    has_item = False
    trash_type = 0

    while True:
        # 1. SAFETY EXIT
        if Button.CENTER in ev3.buttons.pressed():
            break 

        # 2. CHECK SENSORS
        # We check for stations constantly now
        station = get_station_id(line_sensor)
        dist = obstacle_sensor.distance()

        # --- PRIORITY A: STATION DETECTED ---
        if station != 0:
            # We found a station! Identify it.
            if station == 1: ev3.speaker.say("This is Green station")
            elif station == 2: ev3.speaker.say("This is Yellow station")
            elif station == 3: ev3.speaker.say("This is Orange station")

            # Check if we need to DROP here
            if has_item and (station == trash_type):
                deliver_routine()
                has_item = False
                trash_type = 0
                # Drive forward to clear the station logic
                robot.straight(80)
            
            # If not dropping, just WALK FORWARD (Don't turn!)
            else:
                # Drive straight 60mm to cross the color patch
                robot.straight(60)

        # --- PRIORITY B: PICK UP TRASH (Only if empty) ---
        elif (not has_item) and (dist < 50):
            trash_type = pick_up_routine()
            has_item = True

        # --- PRIORITY C: LINE FOLLOWER (Default) ---
        else:
            ref = line_sensor.reflection()
            # Standard PID Follower
            robot.drive(DRIVE_SPEED, (ref - LINE_THRESHOLD) * TURN_GAIN)
        
        wait(10)

finally:
    shutdown()