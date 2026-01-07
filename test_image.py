#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.parameters import Color
from pybricks.tools import wait

# Initialize the EV3 brick.
ev3 = EV3Brick()

# --- Display the image ---
# The draw_image() method loads the image from the specified file path
# and draws it at the specified coordinates (x, y).
# Coordinates (0, 0) is the top-left corner of the screen.

# Optional: Add text over the image
ev3.screen.draw_text(15, 0, "Recyling Robot", text_color=Color.BLACK)

# Keep the program running to display the image until interrupted
wait(10000) # Displays the image for 5 seconds (5000 milliseconds)
