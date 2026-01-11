# config.py
from pybricks.parameters import Color

# --- DRIVE SETTINGS ---
THRESHOLD = 54       
DRIVE_SPEED = 50    
TURN_GAIN = -1.2    # <--- CHANGED to -1.2 for stricter following
BLACK_REFL_THRESHOLD = 20

# --- CORNER LOGIC ---
WHITE_THRESHOLD = 85 
VALID_WHITE_DIST = 50   
CORNER_COOLDOWN = 200   

# --- STATION LOGIC ---
CONFIRM_THRESHOLD = 3
SLOW_PACE = 30  

# --- ARM & CLAMP SETTINGS ---
ARM_SPEED = 200
ARM_SAFE_POS = -270
ARM_DOWN_POS = 5
CLAMP_SPEED = 200
CLAMP_FORCE = 72
CLAMP_OPEN_ANGLE = 70

# --- TRASH DATABASE ---
TRASH_DB = [
    # Plastic -> Station 1 (Red)
    ("Plastic", 6, 100, [Color.BLACK, Color.BROWN, Color.YELLOW, Color.BLUE]), 
    # Paper -> Station 3 (Orange)
    ("Paper",   21, 100, [Color.WHITE, Color.BLUE])
]

# --- STATION NAMES ---
STATION_SEQUENCE = ["Red Station (Plastic)", "Blue Station (Other)", "Orange Station (Paper)"]

# --- STATION CALIBRATION ---

# Station 1: Red (Plastic)
STATION_1_COLOR = [Color.RED]
STATION_1_MIN = 30
STATION_1_MAX = 100 

# Station 2: Blue (Others)
STATION_2_COLOR = [Color.BLUE] 
STATION_2_MIN = 30  
STATION_2_MAX = 40

# Station 3: Orange (Paper)
STATION_3_COLOR = [Color.RED]
STATION_3_MIN = 30
STATION_3_MAX = 100