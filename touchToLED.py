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
import numpy as np # used for 2d framebuffer array

# ----- LED Matrix Configuration -----
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS
PIXEL_PIN = board.D12
BRIGHTNESS = 0.1

# ----- Touch Area Limits -----
TOUCH_WIDTH  = 768        # px 
TOUCH_HEIGHT = 768        # px
FULL_OVERLAY_WIDTH = 1024 # px
BUTTON_AREA_WIDTH = FULL_OVERLAY_WIDTH - TOUCH_WIDTH

# Common color RGB tuples
BLACK      = (0,   0,   0)
DARK_GRAY  = (50,  50,  50)
WHITE      = (255, 255, 255)
RED        = (255, 0,   0)
GREEN      = (0,   255, 0)
BLUE       = (0,   0,   255)
YELLOW     = (255, 255, 0)
CYAN       = (0,   255, 255)
MAGENTA    = (255, 0,   255)

# ----- Orientation toggles (hardcode as needed) -----
SWAP_AXES = True     # set True if row/col appear swapped
HFLIP     = False     # Horizontal Flip Mirror Left/Right
VFLIP     = False      # Vertical Flip Mirror Up/Down

# P2-55: Rotation applied for actual matrix orientation
ROTATE    = 90         # 0, 90, 180, 270 (degrees)

# ----- Orientation toggles for button area -----
ROTATE_BUTTON_INDICATORS = True # set True to rotate button indicators by 90 degrees clockwise
TOUCH_OVERLAY_LEFT_SIDE  = True # set True if button area is located left of the LED matrix

# ----- Button Configuration -----
NUM_BUTTONS = 8

# ----- Create framebuffer array -----
# Match resolution of matrix, each cell has three values for r, g, b
framebuffer = np.zeros((GRID_ROWS, GRID_COLS, 3),  dtype=int)

# ----- Store previous contents of framebuffer for "undo" function -----
prev_framebuffer = np.zeros((GRID_ROWS, GRID_COLS, 3),  dtype=int)

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

    '''
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
    '''

    # clamp (belt & suspenders)
    col = max(0, min(GRID_COLS - 1, col))
    row = max(0, min(GRID_ROWS - 1, row))
    return row, col

def clear_matrix():
    pixels.fill((0, 0, 0))
    pixels.show()

# Set the button indicator LEDs for the given index
def set_button_indicator(button_index, color):

    for i in range(int(GRID_ROWS / NUM_BUTTONS)):

        if ROTATE_BUTTON_INDICATORS:
            led_index = serpentine_index(button_index*(int(GRID_ROWS/NUM_BUTTONS)) + i, GRID_COLS-1)
        else:
            led_index = serpentine_index(GRID_COLS-1, button_index*(int(GRID_ROWS/NUM_BUTTONS)) + i)
        pixels[led_index] = color

    pixels.show()

# Draw the contents of the framebuffer on the LED matrix
def draw_framebuffer():

    for i in range(GRID_ROWS):
        for j in range(GRID_COLS):
            pixels_index = i * GRID_ROWS + j

            # adjust for serpentine layout
            if i % 2 == 0:
                j = GRID_COLS-1 - j

            pixels[pixels_index] = framebuffer[i, j]
    
    pixels.show()

# Erase the contents of the framebuffer
def clear_framebuffer():
    framebuffer[:] = 0

# Set the color of a specific pixel
def set_pixel(x_pos, y_pos, color):

    # Update the framebuffer
    framebuffer[x_pos, y_pos] = color

    # account for serpentine layout
    if x_pos % 2 == 0:
        y_pos = GRID_COLS-1 - y_pos

    # map x and y position to pixel index
    pixels_index = x_pos * GRID_ROWS + y_pos
    pixels[pixels_index] = color

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

    selected_color = (255, 255, 255)

    #Button variables
    selected_button = None
    prev_selected_button = None

    # holding the touchscreen starts a new line
    touch_held = False
    button_held = False

    prev_row = 0
    prev_col = 0

    for event in device.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == ecodes.ABS_MT_POSITION_X:
                x = event.value
            elif event.code == ecodes.ABS_MT_POSITION_Y:
                y = event.value
        elif event.type == ecodes.EV_SYN:
            if x is not None and y is not None:

                # If touch point on LED matrix
                if  ((x >= BUTTON_AREA_WIDTH) and TOUCH_OVERLAY_LEFT_SIDE) or ((x <= TOUCH_WIDTH) and not TOUCH_OVERLAY_LEFT_SIDE):

                    if touch_held == False:
                        touch_held = True
                        print("holding touchscreen")
                        prev_framebuffer[:] = framebuffer

                    if button_held == True:
                        print("button released")
                        button_held = False

                    if TOUCH_OVERLAY_LEFT_SIDE:
                        # Offset touch x value for button area
                        x = x - BUTTON_AREA_WIDTH

                    row, col = map_touch_to_led(x, y)

                    # Only update matrix if LED changes
                    if (prev_row != row) or (prev_col != col):
                    
                        set_pixel(row, col, selected_color)

                    prev_row = row
                    prev_col = col

                    x = y = None

                # Touch point falls over virtual button area
                elif ((x < BUTTON_AREA_WIDTH) and TOUCH_OVERLAY_LEFT_SIDE) or ((x > TOUCH_WIDTH) and not TOUCH_OVERLAY_LEFT_SIDE): 

                    if touch_held == True:
                        print("touch released")
                        touch_held = False

                    if button_held == False:
                        print("holding button")
                        button_held = True

                    # Determine selected button
                    for i in range(NUM_BUTTONS):
                        if y >= i*(TOUCH_HEIGHT / NUM_BUTTONS) and y <= (i+1)*(TOUCH_HEIGHT / NUM_BUTTONS):

                            selected_button = i
                            print("Selected button: ", selected_button)

                    if selected_button is not None:

                        if (prev_selected_button != selected_button) and button_held:
                            draw_framebuffer()

                        match selected_button:
                            # Clear button
                            case 0:
                                print("Clear button selected")
                                set_button_indicator(selected_button, (255, 255, 255))
                                clear_matrix()
                                clear_framebuffer()
                            # Undo button
                            case 1:
                                print("Undo selected")
                                set_button_indicator(selected_button, (255, 255, 255))
                                # restore previous framebuffer
                                framebuffer[:] = prev_framebuffer
                                draw_framebuffer()
                            # Erase button
                            case 2:
                                print("Erase selected")
                                selected_color = (0, 0, 0)
                                set_button_indicator(selected_button, (75, 75, 75))
                            # Red color button
                            case 3:
                                print("Red color selected")
                                selected_color = RED
                                set_button_indicator(selected_button, (selected_color))
                            # Green color button
                            case 4:
                                print("Green color selected")
                                selected_color = GREEN
                                set_button_indicator(selected_button, (selected_color))
                            # Blue color button
                            case 5:
                                print("Blue color selected")
                                selected_color = BLUE
                                set_button_indicator(selected_button, (selected_color))
                            # Purple color button
                            case 6:
                                print("Purple color selected")
                                selected_color = MAGENTA
                                set_button_indicator(selected_button, (selected_color))
                            # White color button
                            case 7:
                                print("White color selected")
                                selected_color = WHITE
                                set_button_indicator(selected_button, (selected_color))
                            case _:
                                print("Unused button")

                        prev_selected_button = selected_button

                    x = y = None

        elif touch_held == True:
            print("touch released")
            touch_held = False

        elif button_held == True:
            print("button released")
            button_held = False
            draw_framebuffer()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        #Ctrl-C to exit and clear matrix
        clear_matrix()
        print("\nExited by user using keyboard interrupt.")
        