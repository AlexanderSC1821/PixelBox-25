from evdev import InputDevice, ecodes
import board
import neopixel
import time

# ----- LED Matrix Configuration -----
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS
PIXEL_PIN = board.D12
BRIGHTNESS = 0.1

# ----- Touch Area Limits -----
TOUCH_WIDTH  = 768   # px (use your device's true max if known)
TOUCH_HEIGHT = 768   # px

# ----- Orientation toggles (hardcode as needed) -----
SWAP_AXES = True     # set True if row/col appear swapped
HFLIP     = False     # mirror left/right
VFLIP     = False      # <-- RECOMMENDED for your symptom (flip vertical)
ROTATE    = 0         # 0, 90, 180, 270 (degrees)

# ----- Setup NeoPixel -----
pixels = neopixel.NeoPixel(
    PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS,
    auto_write=False, pixel_order=neopixel.GRB
)

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

    # --- DO NOT swap top/bottom halves (removed your old 8-row swap) ---

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

def main():
    touch_dev_path = '/dev/input/by-id/usb-UsbHID_SingWon-CTP-V1.18A_6F6A099B1133-event-if00'
    try:
        device = InputDevice(touch_dev_path)
        print(f"Listening on: {device.name}")
    except FileNotFoundError:
        print("Touchscreen device not found.")
        return

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

                print(f"Touch → LED ({row},{col}) → Index {led_index}")

                clear_matrix()
                pixels[led_index] = (255, 0, 0)  # Red
                pixels.show()

                x = y = None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_matrix()
        print("\nExited by user")