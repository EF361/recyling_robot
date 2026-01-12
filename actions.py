# actions.py
from pybricks.parameters import Stop, Color, Button
from pybricks.tools import wait
import config
import hardware

def initialize_robot():
    try:
        hardware.ev3.screen.load_image('logo.png')
    except:
        pass # Skip if logo.png is not found
    
    hardware.ev3.light.on(Color.ORANGE)
    hardware.ev3.speaker.say("Initialize")
    hardware.arm_lift.reset_angle(0)
    hardware.arm_lift.run_target(config.ARM_SPEED, config.ARM_SAFE_POS)
    wait(300)
    hardware.ev3.speaker.say("Clamp")
    hardware.clamp.run_until_stalled(config.CLAMP_SPEED, then=Stop.COAST, duty_limit=config.CLAMP_FORCE)
    hardware.clamp.run_until_stalled(-config.CLAMP_SPEED, then=Stop.HOLD, duty_limit=config.CLAMP_FORCE)
    hardware.clamp.reset_angle(0)
    hardware.ev3.light.on(Color.YELLOW)
    hardware.ev3.speaker.say("Press center")
    while Button.CENTER not in hardware.ev3.buttons.pressed():
        wait(20)
    while Button.CENTER in hardware.ev3.buttons.pressed():
        wait(20)
    hardware.ev3.light.on(Color.GREEN)

def check_station(target_id, color, reflection):
    # Dynamic check based on config.py lists
    if target_id == 1:
        return (color in config.STATION_1_COLOR) and (config.STATION_1_MIN <= reflection <= config.STATION_1_MAX)
    elif target_id == 2:
        return (color in config.STATION_2_COLOR) and (config.STATION_2_MIN <= reflection <= config.STATION_2_MAX)
    elif target_id == 3:
        return (color in config.STATION_3_COLOR) and (config.STATION_3_MIN <= reflection <= config.STATION_3_MAX)
    return False

def park_and_shutdown():
    hardware.robot.stop()
    hardware.ev3.light.on(Color.RED)
    hardware.ev3.speaker.say("Shutdown")
    hardware.clamp.run_until_stalled(-config.CLAMP_SPEED, then=Stop.HOLD, duty_limit=config.CLAMP_FORCE)
    hardware.arm_lift.run_target(config.ARM_SPEED, config.ARM_DOWN_POS)
    wait(300)
    hardware.ev3.speaker.beep()
    
def unload_sequence():
    hardware.robot.stop()
    
    # 1. Turn to Bin
    hardware.robot.turn(150)
    
    # 2. Ultrasonic Approach (Stop at 6cm)
    while hardware.obstacle_sensor.distance() > 60:
        hardware.robot.drive(30, 0) 
        wait(10)
    hardware.robot.stop()
    
    # 3. 🆕 EXTRA NUDGE (Move forward a bit more)
    # Drives slowly (30 speed) for 3 seconds to clear the gap
    hardware.robot.drive(30, 0)
    wait(3000)
    hardware.robot.stop()
    
    # 4. Drop Item
    hardware.arm_lift.run_target(config.ARM_SPEED, config.ARM_SAFE_POS, wait=False)
    hardware.clamp.run_target(config.CLAMP_SPEED, config.CLAMP_OPEN_ANGLE)
    wait(500)
    
    # 5. Reverse (Increased distance slightly to account for the extra nudge)
    hardware.robot.straight(-150)
    
    # 6. Reset Clamp
    hardware.clamp.run_until_stalled(-config.CLAMP_SPEED, duty_limit=40)
    hardware.clamp.reset_angle(0)
    
    # 7. Return Turn
    hardware.robot.turn(-150)
    
def pick_and_drop():
    hardware.robot.stop() 
    wait(100) 
    hardware.ev3.speaker.say("Object")
    
    # 1. Approach
    hardware.robot.drive(30, 0)
    wait(1000) 
    hardware.robot.stop()
    
    # 2. Pick Up Sequence
    hardware.clamp.run_target(config.CLAMP_SPEED, config.CLAMP_OPEN_ANGLE)
    hardware.arm_lift.run_target(config.ARM_SPEED, config.ARM_DOWN_POS)
    
    # ⚠️ FIXED: Added "-" to CLAMP_SPEED to make it CLOSE (Negative direction)
    hardware.clamp.run_until_stalled(-config.CLAMP_SPEED, duty_limit=config.CLAMP_FORCE, then=Stop.HOLD)
    
    hardware.arm_lift.run_target(config.ARM_SPEED, config.ARM_SAFE_POS)
    
    # 3. Identify
    item, col, ref = identify_trash()
    hardware.ev3.speaker.say(item)
    
    return item, col, ref

def identify_trash():
    col = hardware.clamp_sensor.color()
    ref = hardware.clamp_sensor.reflection()
    
    print("[DEBUG] SENSOR: " + str(col) + " | " + str(ref) + "%")

    if ref <= 6:
        return "None", col, ref

    for name, mi, ma, colors in config.TRASH_DB:
        if mi <= ref <= ma and col in colors:
            return name, col, ref
            
    return "Others", col, ref