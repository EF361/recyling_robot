#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.parameters import Port, Button, Color, Stop
from pybricks.tools import wait

# =============================================================================
# SETTINGS
# =============================================================================
ARM_SPEED = 200
ARM_SAFE_POS = -202    # UP / SAFE
ARM_DOWN_POS = 5

CLAMP_SPEED = 200
CLAMP_FORCE = 40

# =============================================================================
# SETUP
# =============================================================================
ev3 = EV3Brick()
ev3.speaker.set_volume(100)

arm_lift = Motor(Port.B)
clamp = Motor(Port.A)

# =============================================================================
# INITIALIZE
# =============================================================================
def initialize():
    ev3.light.on(Color.ORANGE)
    ev3.speaker.say("Initialize")

    # 1️⃣ ARM: move to SAFE position (same logic as your working file)
    arm_lift.reset_angle(0)
    arm_lift.run_target(ARM_SPEED, ARM_SAFE_POS)
    wait(300)

    # 2️⃣ CLAMP calibration (open → close)
    ev3.speaker.say("Clamp")

    clamp.run_until_stalled(
        CLAMP_SPEED,
        then=Stop.COAST,
        duty_limit=CLAMP_FORCE
    )

    clamp.run_until_stalled(
        -CLAMP_SPEED,
        then=Stop.HOLD,
        duty_limit=CLAMP_FORCE
    )

    clamp.reset_angle(0)

    ev3.light.on(Color.YELLOW)
    ev3.speaker.say("Press center")

    # 3️⃣ Wait for CENTER button
    while Button.CENTER not in ev3.buttons.pressed():
        wait(20)

# =============================================================================
# SHUTDOWN
# =============================================================================
def shutdown():
    ev3.light.on(Color.RED)
    ev3.speaker.say("Shutdown")

    # Ensure clamp closed
    clamp.run_until_stalled(
        -CLAMP_SPEED,
        then=Stop.HOLD,
        duty_limit=CLAMP_FORCE
    )

    # Lower arm
    arm_lift.run_target(ARM_SPEED, ARM_DOWN_POS)
    wait(300)

    ev3.speaker.beep()

# =============================================================================
# MAIN (RUN ONCE)
# =============================================================================
initialize()
shutdown()
