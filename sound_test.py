#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.tools import wait

# Initialize the EV3 Brick
ev3 = EV3Brick()

# =============================================================================
# 🔊 VOICE CONFIGURATION (FIXED)
# =============================================================================

# 1. Set Volume SEPARATELY (0-100)
ev3.speaker.set_volume(100)

# 2. Set Voice Options (Speed and Pitch ONLY)
# Removed 'volume' from this list because it caused the crash.
ev3.speaker.set_speech_options(speed=120, pitch=100)

# =============================================================================
# 🧪 THE SOUND TEST
# =============================================================================

print("Test Started...")

# 1. Beep Test
ev3.speaker.beep()
wait(500)

# 2. Voice Test
ev3.speaker.say("Ob-ject de-tec-ted")
wait(500)

ev3.speaker.say("This is Plas-tick")
wait(500)

ev3.speaker.say("This is Pay-purr")
wait(500)

ev3.speaker.say("This is Met-tull")
wait(500)

print("Test Complete.")