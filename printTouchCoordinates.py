from evdev import InputDevice, categorize, ecodes
import os

# Adjust this to match your touchscreen device path
TOUCH_DEVICE = '/dev/input/by-id/usb-UsbHID_SingWon-CTP-V1.18A_6F6A099B1133-event-if00'

# Open the touchscreen device
try:
    device = InputDevice(TOUCH_DEVICE)
    print(f"Listening for touches on: {device.name}")
except FileNotFoundError:
    print(f"Device not found at {TOUCH_DEVICE}")
    exit(1)

x, y = None, None
def map_to_led_matrix(x, y,
                      matrix_w=16, matrix_h=16,
                      touch_active_w=768, touch_active_h=768):
    """
    Maps touchscreen X/Y input from a rectangular touchscreen onto a square LED matrix
    that's physically located at the left edge (x = 0).
    """
    # Clamp inputs to the active LED matrix region
    x = min(x, touch_active_w)
    y = min(y, touch_active_h)

    led_x = int((x / touch_active_w) * matrix_w)
    led_y = int((y / touch_active_h) * matrix_h)

    # Bound check
    led_x = max(0, min(matrix_w - 1, led_x))
    led_y = max(0, min(matrix_h - 1, led_y))

    return led_x, led_y

for event in device.read_loop():
    if event.type == ecodes.EV_ABS:
        if event.code == ecodes.ABS_MT_POSITION_X:
            x = event.value
        elif event.code == ecodes.ABS_MT_POSITION_Y:
            y = event.value
    elif event.type == ecodes.EV_SYN:
       
        # A full touch event (sync) — only print if both coords are captured
        if x is not None and y is not None:
            led_x, led_y = map_to_led_matrix(x, y)
            if x > 768:
                #Touches outside the active area are not considered
                print("Touch outside active area, ignoring.")
                x, y = None, None
                continue
            print(f"Touch at: X={led_x}, Y={led_y} (Raw: X={x}, Y={y})")

            # Reset coordinates after printing
            x, y = None, None
            