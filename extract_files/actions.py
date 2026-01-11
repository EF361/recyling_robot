from pybricks.parameters import Color, Button, Stop
from pybricks.tools import wait
from hardware import ev3, robot, arm_lift, clamp, clamp_sensor, left_motor, right_motor
import config

def initialize():
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("System Start")
    
    arm_lift.reset_angle(0)
    arm_lift.run_target(config.ARM_SPEED, config.ARM_SAFE_POS, then=Stop.BRAKE)
    
    clamp.run_until_stalled(-config.CLAMP_SPEED, duty_limit=40)
    clamp.run_until_stalled(config.CLAMP_SPEED, duty_limit=40)
    clamp.reset_angle(0)
    clamp.run_target(config.CLAMP_SPEED, -5, then=Stop.COAST)
    
    robot.reset()
    ev3.light.on(Color.GREEN)
    ev3.speaker.say("Ready")
    
    while Button.CENTER not in ev3.buttons.pressed(): wait(20)
    while Button.CENTER in ev3.buttons.pressed(): wait(20)

def identify_trash():
    final_decision = "None"
    for i in range(5):
        col, ref = clamp_sensor.color(), clamp_sensor.reflection()
        for name, mi, ma, colors in config.TRASH_DB:
            if mi <= ref <= ma and col in colors:
                final_decision = name
        wait(200)
    return final_decision

def pick_and_drop():
    robot.stop()
    wait(100)
    ev3.speaker.say("Object")
    robot.drive(30, 0)
    wait(1000)
    robot.stop()
    
    clamp.run_target(config.CLAMP_SPEED, config.CLAMP_OPEN_ANGLE)
    arm_lift.run_target(config.ARM_SPEED, config.ARM_DOWN_POS)
    clamp.run_until_stalled(config.CLAMP_SPEED, then=Stop.HOLD, duty_limit=config.CLAMP_FORCE)
    arm_lift.run_target(config.ARM_SPEED, config.ARM_SAFE_POS)
    
    item = identify_trash()
    ev3.speaker.say(item)
    
    if item != "None":
        wait(5000)
        clamp.run_target(config.CLAMP_SPEED, config.CLAMP_OPEN_ANGLE)
        wait(1000)
        clamp.run_until_stalled(config.CLAMP_SPEED, duty_limit=config.CLAMP_FORCE)
    else:
        clamp.run_until_stalled(config.CLAMP_SPEED, duty_limit=config.CLAMP_FORCE)

def check_station_logic(target_name, color, reflection):
    if target_name == "Dark Blue Station":
        return color == Color.BLUE and 18 <= reflection <= 25
    elif target_name == "Light Green Station":
        return color == Color.WHITE and 48 <= reflection <= 60
    elif target_name == "Orange Station":
        return color == Color.RED and reflection >= 95
    return False

def shutdown():
    ev3.light.on(Color.RED)
    robot.stop()
    ev3.speaker.say("Shutdown")
    clamp.run_until_stalled(config.CLAMP_SPEED, duty_limit=config.CLAMP_FORCE)
    arm_lift.run_target(config.ARM_SPEED, config.ARM_DOWN_POS)
    left_motor.stop()
    right_motor.stop()
    ev3.speaker.beep()