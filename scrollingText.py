'''
Code Example Use:
import scrollingText
scrollingText.main("text")


'''


import time
import board
import neopixel
import colorsys

# --- Matrix Config ---
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS
BRIGHTNESS = 0.1
VERTICAL_OFFSET = 4  # shift down so 7px font is centered in 16px tall grid

# --- NeoPixel Setup ---
pixels = neopixel.NeoPixel(board.D12, NUM_PIXELS, auto_write=False, brightness=BRIGHTNESS)

# --- Font (same as your version) ---
FONT_5x7 = {
    # --- Uppercase ---
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "B": ["11110","10001","11110","10001","10001","10001","11110"],
    "C": ["01111","10000","10000","10000","10000","10000","01111"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","11110","10000","10000","10000","11111"],
    "F": ["11111","10000","11110","10000","10000","10000","10000"],
    "G": ["01111","10000","10000","10011","10001","10001","01111"],
    "H": ["10001","10001","11111","10001","10001","10001","10001"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "J": ["11111","00010","00010","00010","00010","10010","01100"],
    "K": ["10001","10010","11100","10010","10001","10001","10001"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "M": ["10001","11011","10101","10101","10001","10001","10001"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","11110","10000","10000","10000","10000"],
    "Q": ["01110","10001","10001","10001","10101","10010","01101"],
    "R": ["11110","10001","11110","10010","10001","10001","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "X": ["10001","10001","01010","00100","01010","10001","10001"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "Z": ["11111","00001","00010","00100","01000","10000","11111"],

    # --- Digits ---
    "0": ["01110","10001","10011","10101","11001","10001","01110"],
    "1": ["00100","01100","00100","00100","00100","00100","01110"],
    "2": ["01110","10001","00001","00010","00100","01000","11111"],
    "3": ["11111","00010","00100","00010","00001","10001","01110"],
    "4": ["00010","00110","01010","10010","11111","00010","00010"],
    "5": ["11111","10000","11110","00001","00001","10001","01110"],
    "6": ["01110","10001","10000","11110","10001","10001","01110"],
    "7": ["11111","00001","00010","00100","01000","01000","01000"],
    "8": ["01110","10001","10001","01110","10001","10001","01110"],
    "9": ["01110","10001","10001","01111","00001","10001","01110"],

    # --- Lowercase ---
    "a": ["00000","00000","01110","00001","01111","10001","01111"],
    "b": ["10000","10000","11110","10001","10001","10001","11110"],
    "c": ["00000","00000","01111","10000","10000","10000","01111"],
    "d": ["00001","00001","01111","10001","10001","10001","01111"],
    "e": ["00000","00000","01110","10001","11111","10000","01110"],
    "f": ["00110","01001","01000","11110","01000","01000","01000"],
    "g": ["00000","00000","01111","10001","01111","00001","11110"],
    "h": ["10000","10000","11110","10001","10001","10001","10001"],
    "i": ["00100","00000","01100","00100","00100","00100","01110"],
    "j": ["00010","00000","00110","00010","00010","10010","01100"],
    "k": ["10000","10000","10010","10100","11000","10100","10010"],
    "l": ["11000","01000","01000","01000","01000","01000","11110"],
    "m": ["00000","00000","11010","10101","10101","10001","10001"],
    "n": ["00000","00000","11110","10001","10001","10001","10001"],
    "o": ["00000","00000","01110","10001","10001","10001","01110"],
    "p": ["00000","00000","11110","10001","10001","11110","10000"],
    "q": ["00000","00000","01111","10001","10001","01111","00001"],
    "r": ["00000","00000","10111","11000","10000","10000","10000"],
    "s": ["00000","00000","01111","10000","01110","00001","11110"],
    "t": ["01000","01000","11110","01000","01000","01001","00110"],
    "u": ["00000","00000","10001","10001","10001","10001","01111"],
    "v": ["00000","00000","10001","10001","10001","01010","00100"],
    "w": ["00000","00000","10001","10001","10101","10101","01010"],
    "x": ["00000","00000","10001","01010","00100","01010","10001"],
    "y": ["00000","00000","10001","10001","01111","00001","11110"],
    "z": ["00000","00000","11111","00010","00100","01000","11111"],

    # --- Space ---
    " ": ["00000","00000","00000","00000","00000","00000","00000"],
}

# --- Font Helpers ---
def char_to_bitmap(char):
    """Convert single character into 2D list (rows of 0/1)."""
    rows = FONT_5x7.get(char, FONT_5x7[" "])
    return [[int(bit) for bit in row] for row in rows]

def text_to_bitmap(text):
    """Convert text string into one big bitmap row (7 tall, variable wide)."""
    bitmap = [[] for _ in range(7)]

    # Add left padding (blank columns equal to display width)
    for r in range(7):
        bitmap[r] += [0] * GRID_COLS

    # Build each character with 1px spacing
    for char in text:
        char_bitmap = char_to_bitmap(char)
        for r in range(7):
            bitmap[r] += char_bitmap[r] + [0]

    # Add right padding (blank columns equal to display width)
    for r in range(7):
        bitmap[r] += [0] * GRID_COLS

    return bitmap

# --- Pixel Mapping (serpentine) ---
def set_pixel(row, col, color):
    """Serpentine wiring with reversed row order."""
    if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
        if row % 2 == 0:
            # even row: right to left
            idx = row * GRID_COLS + (GRID_COLS - 1 - col)
        else:
            # odd row: left to right
            idx = row * GRID_COLS + col
        pixels[idx] = color

# --- Color Helpers ---
def hsv_to_rgb(h, s, v):
    """Convert HSV (0-1 floats) to RGB (0-255 ints)."""
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return int(r * 255), int(g * 255), int(b * 255)

def rainbow_colors(n):
    """Generate n evenly spaced colors across the HSV rainbow."""
    return [hsv_to_rgb(i / n, 1.0, 1.0) for i in range(n)]

# --- Drawing ---
def display_window(bitmap, offset, colors_per_char):
    char_width = 6  # 5px font + 1px spacing
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            set_pixel(row, col, (0, 0, 0))  # clear background
            if (row - VERTICAL_OFFSET) in range(len(bitmap)) and (col + offset) < len(bitmap[0]):
                if bitmap[row - VERTICAL_OFFSET][col + offset] == 1:
                    char_index = (col + offset) // char_width
                    # Clamp to valid range
                    if char_index >= len(colors_per_char):
                        char_index = len(colors_per_char) - 1
                    set_pixel(row, col, colors_per_char[char_index])
    pixels.show()


def scroll_text(text, speed=0.1):
    bitmap = text_to_bitmap(text)
    text_width = len(bitmap[0])

    # rainbow length = number of characters in the text
    num_chars = len(text)
    colors_per_char = rainbow_colors(num_chars)

    for offset in range(-GRID_COLS, text_width):
        display_window(bitmap, offset, colors_per_char)
        time.sleep(speed)


# --- Example Usage ---
def main(text_to_scroll:str):
    try:
        scroll_text(text_to_scroll, speed=0.08)

        pixels.fill((0, 0, 0))
        pixels.show()
    except KeyboardInterrupt:
        pixels.fill((0, 0, 0))
        pixels.show()
        print("Stopped.")
        
if __name__ == "__main__":
    main()

