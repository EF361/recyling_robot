#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import ColorSensor
from pybricks.parameters import Port, Button, Color
from pybricks.tools import wait

# =============================================================================
# 🔌 SETUP
# =============================================================================
ev3 = EV3Brick()
# Make sure this matches your sensor port!
line_sensor = ColorSensor(Port.S3) 

# =============================================================================
# 🛠️ HELPER
# =============================================================================
def wait_for_center():
    """Waits for the button to be PRESSED and then RELEASED."""
    # 1. Wait for Press
    while Button.CENTER not in ev3.buttons.pressed():
        wait(10)
    # 2. Wait for Release (Debounce)
    while Button.CENTER in ev3.buttons.pressed():
        wait(10)

# =============================================================================
# 🚀 MAIN LOOP
# =============================================================================
ev3.speaker.set_volume(100)
print("\n" + "="*40)
print("   SENSOR DATA LOGGER")
print("   1. Press CENTER to START")
print("   2. Press CENTER to STOP")
print("="*40 + "\n")

while True:
    # --- PHASE 1: IDLE (Waiting to Start) ---
    ev3.light.on(Color.ORANGE)
    print(">>> Ready. Press CENTER to Record.")
    
    wait_for_center() # Helper function handles press & release
    
    # --- PHASE 2: RECORDING ---
    ev3.speaker.beep()
    ev3.light.on(Color.GREEN)
    print("\n--- NEW RECORDING ---")
    print("Color Code | Refl | Amb")
    
    while True:
        # 1. Check if user wants to STOP
        if Button.CENTER in ev3.buttons.pressed():
            # Wait for release so we don't restart immediately
            while Button.CENTER in ev3.buttons.pressed(): wait(10)
            break # Exit the recording loop
            
        # 2. Read Data
        c = line_sensor.color()
        r = line_sensor.reflection()
        a = line_sensor.ambient()
        
        # 3. Print Data
        # Format: Color(12 chars) | Refl(4 chars) | Amb(4 chars)
        print("{:<12} | {:<4} | {:<4}".format(str(c), r, a))
        
        wait(200) # 5 readings per second
        
    # --- PHASE 3: STOPPED ---
    print("--- STOPPED ---\n")
    ev3.speaker.beep()
    wait(500) # Short pause before allowing next start