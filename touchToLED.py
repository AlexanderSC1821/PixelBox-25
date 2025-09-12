# =====================================================================
#                   Pixelbox - touchToLED.py
#   touchToLED.py
#   Pixelbox
#   Author: Alex Closson
#   Date: 09/08/2025
#   Last Update: 09/08/2025
#   Version: 1.0.0
#   Summary: File to test functionality between touchscreen and LED Matrix.
# =====================================================================


from evdev import InputDevice, ecodes #Touchscreen input library
import board #Pin definitions for Raspberry Pi
import neopixel #LED Matrix library
import time #Time library for delays

# ----- LED Matrix Configuration -----
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS
PIXEL_PIN = board.D12
BRIGHTNESS = 0.1

# ----- Touch Area Limits -----
TOUCH_WIDTH  = 768   # px 
TOUCH_HEIGHT = 768   # px

# ----- Orientation toggles (hardcode as needed) -----
SWAP_AXES = True     # set True if row/col appear swapped
HFLIP     = False     # Horizontal Flip Mirror Left/Right
VFLIP     = False      # Vertical Flip Mirror Up/Down
ROTATE    = 0         # 0, 90, 180, 270 (degrees)

# ----- Setup NeoPixel -----
pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS,
    auto_write=False, pixel_order=neopixel.GRB
)

# ----- Helper Functions -----
def serpentine_index(row, col):
    # row-wise serpentine
    if row % 2 == 0:
        return row * GRID_COLS + col
    else:
        return row * GRID_COLS + (GRID_COLS - 1 - col)

def map_touch_to_led(x, y):
    # scale raw touch to grid cell (use -1 to avoid hitting 16)
    col = int((x / max(1, TOUCH_WIDTH  - 1)) * (GRID_COLS - 1) + 0.5)
    row = int((y / max(1, TOUCH_HEIGHT - 1)) * (GRID_ROWS - 1) + 0.5)


    # apply transforms
    if SWAP_AXES:
        row, col = col, row

    # rotations (about top-left origin)
    if ROTATE == 90:
        row, col = col, (GRID_COLS - 1) - row
    elif ROTATE == 180:
        row, col = (GRID_ROWS - 1) - row, (GRID_COLS - 1) - col
    elif ROTATE == 270:
        row, col = (GRID_ROWS - 1) - col, row

    if HFLIP:
        col = (GRID_COLS - 1) - col
    if VFLIP:
        row = (GRID_ROWS - 1) - row

    # clamp (belt & suspenders)
    col = max(0, min(GRID_COLS - 1, col))
    row = max(0, min(GRID_ROWS - 1, row))
    return row, col

def clear_matrix():
    pixels.fill((0, 0, 0))
    pixels.show()

# ----- Main Loop -----
def main():
    #Path of touchscreen device. Adjust as needed.
    touch_dev_path = '/dev/input/by-id/usb-UsbHID_SingWon-CTP-V1.18A_6F6A099B1133-event-if00'
    try:
        device = InputDevice(touch_dev_path) #Initialize touchscreen device
        print(f"Listening on: {device.name}")
    except FileNotFoundError:
        print("Touchscreen device not found.")
        return

    #Clear the screen initially
    clear_matrix()
    x = y = None

    for event in device.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_POSITION_X:
                x = event.value
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                y = event.value
        elif event.type == ecodes.EV_SYN:
            if x is not None and y is not None:
                row, col = map_touch_to_led(x, y)
                led_index = serpentine_index(row, col)

                #Light up corresponding LED and print to terminal
                print(f"Touch → LED ({row},{col}) → Index {led_index}")
                pixels[led_index] = (255, 0, 0)  # Red
                pixels.show()

                x = y = None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        #Ctrl-C to exit and clear matrix
        clear_matrix()
        print("\nExited by user using keyboard interrupt.")
        