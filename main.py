#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, UltrasonicSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait, StopWatch
from pybricks.robotics import DriveBase

# =============================================================================
# ⚙️ CONFIGURATION / CONSTANTS (TUNE THESE NUMBERS!)
# =============================================================================

# 1. Physical Dimensions (Measure your robot for best accuracy)
WHEEL_DIAMETER = 56    # Millimeters (Standard EV3 wheel is 56)
AXLE_TRACK = 114       # Millimeters (Distance between the centers of two wheels)

# 2. Speeds
DRIVE_SPEED = 150      # mm/s (Standard driving speed)
TURN_SPEED = 100       # deg/s (Turning speed)
ARM_SPEED = 200        # deg/s (Speed of lifting/clamping)

# 3. Thresholds
OBSTACLE_DIST = 50     # mm (5cm) - Stop distance for trash
LINE_THRESHOLD = 35    # Reflected light value (Black < 35 < White)

# 4. Delivery Distances
DIST_TO_BIN = 300      # mm (30cm) - Distance to drive forward to the bin
DROP_ANGLE = 90        # degrees - Angle to turn towards the bin

# =============================================================================
# 🔌 HARDWARE SETUP
# =============================================================================

# Initialize the EV3 Brick
ev3 = EV3Brick()
ev3.speaker.beep() # Beep to show we are ready

# Initialize Motors
# NOTE: Check if your motors need 'positive_direction=Direction.COUNTERCLOCKWISE'
# if they run backwards.
left_motor = Motor(Port.D) 
right_motor = Motor(Port.C)
arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

# Initialize the DriveBase (Handles all movement math automatically)
robot = DriveBase(left_motor, right_motor, wheel_diameter=WHEEL_DIAMETER, axle_track=AXLE_TRACK)
robot.settings(DRIVE_SPEED, TURN_SPEED)

# Initialize Sensors
# Port 1: Obstacle (Ultrasonic)
# Port 2: Trash Scanner (Color Sensor on Clamp)
# Port 3: Line Reader (Color Sensor on Floor)
obstacle_sensor = UltrasonicSensor(Port.S1)
clamp_sensor = ColorSensor(Port.S2)
line_sensor = ColorSensor(Port.S3)

# =============================================================================
# 🧠 FUNCTIONS
# =============================================================================

def line_follower_step():
    """
    Simple P-Controller for smooth line following.
    Adjusts steering based on how 'black' or 'white' the floor is.
    """
    # Calculate the deviation from the threshold
    # Reflection: Black=10, White=80. Threshold=45.
    reflection = line_sensor.reflection()
    deviation = reflection - LINE_THRESHOLD
    
    # Turn gain: Higher number = sharper turns (more jittery)
    # Lower number = smoother turns (might miss tight corners)
    turn_rate = deviation * 1.2 
    
    # Drive forward while turning
    robot.drive(DRIVE_SPEED, turn_rate)

def pick_up_routine():
    """
    Sequence: Stop -> Open -> Lower -> Close -> Raise -> SCAN COLOR -> Return Type
    """
    # 1. Grab Logic (Same as before)
    clamp.run_time(ARM_SPEED, 1000)          # Open
    arm_lift.run_angle(ARM_SPEED, 90)        # Lower
    clamp.run_time(-ARM_SPEED, 1000)         # Close
    arm_lift.run_target(ARM_SPEED, 0)        # Raise
    
    wait(500) # Pause to let item stabilize
    
    # 2. Identify Logic (The Speaking Part)
    detected = clamp_sensor.color()
    item_type = 0
    
    if detected == Color.GREEN:
        # 🗣️ NEW: Specific Voice Line
        ev3.speaker.say("This is plastic")
        item_type = 1
        
    elif detected == Color.YELLOW:
        # 🗣️ NEW: Specific Voice Line
        ev3.speaker.say("This is paper")
        item_type = 2
        
    elif detected == Color.RED:
        # 🗣️ NEW: Specific Voice Line
        ev3.speaker.say("This is metal") # Or "This is Aluminum"
        item_type = 3 
        
    else:
        ev3.speaker.say("Unknown object")
        item_type = 3 

    return item_type

def deliver_routine():
    """
    Sequence: Turn 90 -> Drive -> Drop -> Reverse -> Turn 180 (or back 90)
    """
    robot.stop()
    ev3.speaker.beep(500, 100) # High pitch beep
    
    # 1. Turn towards bin (Right turn = positive angle)
    robot.turn(DROP_ANGLE)
    
    # 2. Drive to bin
    robot.straight(DIST_TO_BIN)
    
    # 3. Drop Item
    clamp.run_time(ARM_SPEED, 1000) # Open
    wait(500)
    
    # 4. Return
    robot.straight(-DIST_TO_BIN) # Drive backwards same distance
    
    # 5. Realign to line
    # NOTE: If we turned Right to face bin, turning Left (negative) brings us back.
    robot.turn(-DROP_ANGLE) 
    
    # Close clamp to be ready for next one (optional)
    clamp.run_time(-ARM_SPEED, 1000)

# =============================================================================
# 🚀 MAIN PROGRAM LOOP
# =============================================================================

# State Variables
has_item = False
trash_type = 0 # 0=None, 1=Green, 2=Yellow, 3=Red

# Initial Arm Setup (Safety)
ev3.light.on(Color.ORANGE)
arm_lift.run_target(ARM_SPEED, 0) # Reset arm to 'zero' position
wait(1000)
ev3.light.on(Color.GREEN)

while True:
    # --- MODE A: SEARCHING ---
    if not has_item:
        # Check for obstacle
        dist = obstacle_sensor.distance()
        
        if dist < OBSTACLE_DIST:
            # 🗣️ NEW: Say "Object Detected" immediately
            robot.stop()
            ev3.speaker.say("Object detected") 
            
            # Then start the pickup
            trash_type = pick_up_routine()
            has_item = True
        else:
            # No trash, follow the line
            line_follower_step()

    # --- MODE B: CARRYING (DELIVERY) ---
    else:
        # Check floor color for Bin Markers
        floor_color = line_sensor.color()
        
        # Check Matches
        match_found = False
        
        if floor_color == Color.GREEN and trash_type == 1:
            match_found = True
        elif floor_color == Color.YELLOW and trash_type == 2:
            match_found = True
        elif floor_color == Color.RED and trash_type == 3:
            match_found = True
            
        if match_found:
            # We are at the correct bin!
            deliver_routine()
            
            # Reset state
            has_item = False
            trash_type = 0
            
            # Move forward a tiny bit to get past the color marker
            # so we don't detect it again immediately
            robot.straight(50) 
            
        else:
            # Not at the right bin yet, keep following line
            line_follower_step()

    # Small wait to save CPU
    wait(10)