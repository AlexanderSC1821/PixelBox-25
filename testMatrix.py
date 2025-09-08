# =====================================================================
#                   Pixelbox - testMatrix.py
#   testMatrix.py
#   Pixelbox
#   Author: Alex Closson
#   Date: 09/08/2025
#   Last Update: 09/08/2025
#   Version: 1.0.0
#   Summary: File to test the LED matrix functionality by illuminating the first 10 LEDs with a green light and then turning them off.
# =====================================================================


import time
import board
import neopixel

# --- Config ---
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS

# --- NeoPixel setup ---
pixels = neopixel.NeoPixel(board.D12, NUM_PIXELS, auto_write=False, brightness=0.2)

try:
    print("Lighting first 10 LEDs green...")
    for i in range(10):
        pixels[i] = (0, 255, 0)  # Green
    pixels.show()

    time.sleep(2)  # hold for 2 seconds

    print("Turning all LEDs off...")
    pixels.fill((0, 0, 0))
    pixels.show()

except KeyboardInterrupt:
    pixels.fill((0, 0, 0))
    pixels.show()
    print("Stopped.")
