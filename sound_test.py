#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

# Initialize the EV3 Brick
ev3 = EV3Brick()

# =============================================================================
# 🔊 VOICE CONFIGURATION
# =============================================================================
# Tuning the voice to sound less "weird" and more robotic/clear.
# Speed: 80 (Slightly slower is easier to understand)
# Pitch: 60 (Higher pitch cuts through motor noise better)
ev3.speaker.set_speech_options(volume=100, speed=80, pitch=60)

# =============================================================================
# 🧪 THE SOUND TEST
# =============================================================================

print("Test Started...")

# 1. Beep Test (To confirm speaker works)
ev3.speaker.beep()
wait(500)

# 2. Voice Test (Using Phonetic Spelling)
# We spell words wrong on purpose so the robot pronounces them correctly.

# "Object detected" -> "Ob-ject de-tec-ted"
ev3.speaker.say("Ob-ject de-tec-ted")
wait(500)

# "This is plastic" -> "This is Plas-tick"
ev3.speaker.say("This is Plas-tick")
wait(500)

# "This is paper" -> "This is Pay-purr"
ev3.speaker.say("This is Pay-purr")
wait(500)

# "This is metal" -> "This is Met-tull"
ev3.speaker.say("This is Met-tull")
wait(500)

# "This is Aluminum" -> "This is Al-loo-min-knee-um"
ev3.speaker.say("This is Al-loo-min-knee-um")
wait(500)

print("Test Complete.")