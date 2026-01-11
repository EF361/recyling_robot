from pybricks.parameters import Color

# --- NAVIGATION SETTINGS ---
THRESHOLD = 44
DRIVE_SPEED = 50
TURN_GAIN = -1.2
WHITE_THRESHOLD = 75
VALID_WHITE_DIST = 50
CORNER_COOLDOWN = 200
CONFIRM_THRESHOLD = 5
SLOW_PACE = 30

# --- HARDWARE SETTINGS ---
ARM_SPEED = 200
ARM_SAFE_POS = -260
ARM_DOWN_POS = 0
CLAMP_SPEED = 200
CLAMP_FORCE = 80
CLAMP_OPEN_ANGLE = -70

# --- DATABASE & SEQUENCES ---
TRASH_DB = [
    ("None",    0, 5,   [None, Color.BLACK]),
    ("Plastic", 6, 100, [Color.BLACK, Color.BROWN, Color.YELLOW, Color.BLUE]),
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

STATION_SEQUENCE = ["Plastic Station", "Paper Station", "Other Station"]