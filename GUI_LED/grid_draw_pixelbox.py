import tkinter as tk
from evdev import InputDevice, ecodes
import board
import neopixel

# =========================
# Config
# =========================
GRID_ROWS = 16
GRID_COLS = 16
NUM_PIXELS = GRID_ROWS * GRID_COLS

PIXEL_PIN   = board.D12
BRIGHTNESS  = 0.15
PIXEL_ORDER = neopixel.GRB

# Hardcode your stable touch area
TOUCH_WIDTH  = 768
TOUCH_HEIGHT = 768
TOUCH_DEV    = '/dev/input/by-id/usb-UsbHID_SingWon-CTP-V1.18A_6F6A099B1133-event-if00'

# Orientation (from your working simple script)
SWAP_AXES = True
HFLIP     = False
VFLIP     = False
ROTATE    = 0   # 0 / 90 / 180 / 270

# Fill full screen width with the grid cells
FILL_WIDTH = True


# =========================
# Helpers
# =========================
def color_hex_to_rgb(hex_color: str):
    h = hex_color.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

def serpentine_index(row, col):
    # row-wise serpentine
    if row % 2 == 0:
        return row * GRID_COLS + col
    else:
        return row * GRID_COLS + (GRID_COLS - 1 - col)

def orient(row, col):
    """Apply SWAP/ROTATE/FLIP to map GUI (row,col) to physical matrix (row,col)."""
    R, C = GRID_ROWS, GRID_COLS
    # 1) swap
    if SWAP_AXES:
        row, col = col, row
    # 2) rotate (square grid)
    if ROTATE == 90:
        row, col = col, (C - 1) - row
    elif ROTATE == 180:
        row, col = (R - 1) - row, (C - 1) - col
    elif ROTATE == 270:
        row, col = (R - 1) - col, row
    # 3) flips
    if HFLIP:
        col = (C - 1) - col
    if VFLIP:
        row = (R - 1) - row
    # clamp
    row = max(0, min(R - 1, row))
    col = max(0, min(C - 1, col))
    return row, col


# =========================
# App
# =========================
class LEDTouchGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Touch → LED Painter")

        # Compute cell size
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        if FILL_WIDTH:
            self.CELL = max(1, sw // GRID_COLS)  # fills screen width
        else:
            self.CELL = max(1, min(sw // GRID_COLS, sh // GRID_ROWS))

        # NeoPixels
        self.pixels = neopixel.NeoPixel(
            PIXEL_PIN, NUM_PIXELS, brightness=BRIGHTNESS,
            auto_write=False, pixel_order=PIXEL_ORDER
        )
        self.pixels.fill((0, 0, 0)); self.pixels.show()

        # UI: Canvas on top
        self.canvas = tk.Canvas(
            root,
            width=GRID_COLS * self.CELL,
            height=GRID_ROWS * self.CELL,
            bg="black"
        )
        self.canvas.pack(side=tk.TOP, pady=6)

        # Draw grid
        self.rects = {}
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x1, y1 = c * self.CELL, r * self.CELL
                x2, y2 = x1 + self.CELL, y1 + self.CELL
                self.rects[(r, c)] = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="black", outline="gray"
                )

        # Controls
        ctrl = tk.Frame(root); ctrl.pack(side=tk.TOP, pady=6)
        tk.Button(ctrl, text="Clear", command=self.clear).pack(side=tk.LEFT, padx=4)
        tk.Button(ctrl, text="Exit", command=self.exit).pack(side=tk.LEFT, padx=4)

        # Simple color presets
        pal = tk.Frame(root); pal.pack(side=tk.TOP, pady=6)
        for name, hexcol in [
            ("Red", "#ff0000"),
            ("Green", "#00ff00"),
            ("Blue", "#0000ff"),
            ("Yellow", "#ffff00"),
            ("White", "#ffffff"),
            ("Cyan", "#00ffff"),
            ("Magenta", "#ff00ff"),
        ]:
            tk.Button(pal, text=name, bg=hexcol, command=lambda h=hexcol: self.set_color(h)).pack(side=tk.LEFT, padx=3)

        self.current_hex = "#00ff00"
        self.current_rgb = color_hex_to_rgb(self.current_hex)

        # Mouse drawing (optional)
        self.drawing = False
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Touch device state
        self.dev = None
        self.use_mt = False         # prefer ABS_MT_* if available
        self.touch_down = False     # gated by BTN_TOUCH or MT tracking
        self.x = None               # last X for current frame
        self.y = None               # last Y for current frame

        self.init_touch()
        self.poll_touch()  # start polling loop (no threads)

    # ---- UI actions ----
    def set_color(self, hexcol):
        self.current_hex = hexcol
        self.current_rgb = color_hex_to_rgb(hexcol)

    def clear(self):
        self.pixels.fill((0, 0, 0)); self.pixels.show()
        for rid in self.rects.values():
            self.canvas.itemconfig(rid, fill="black")

    def exit(self):
        try:
            self.pixels.fill((0, 0, 0)); self.pixels.show()
        finally:
            self.root.destroy()

    # ---- Mouse (optional) ----
    def on_mouse_down(self, e):
        self.drawing = True
        self.paint_from_canvas(e.x, e.y)

    def on_mouse_move(self, e):
        if self.drawing:
            self.paint_from_canvas(e.x, e.y)

    def on_mouse_up(self, e):
        self.drawing = False

    def paint_from_canvas(self, px, py):
        col = px // self.CELL
        row = py // self.CELL
        if (row, col) not in self.rects:
            return
        mr, mc = orient(row, col)
        idx = serpentine_index(mr, mc)
        self.pixels[idx] = self.current_rgb
        self.pixels.show()
        self.canvas.itemconfig(self.rects[(row, col)], fill=self.current_hex)

    # ---- Touch setup & polling (no threads, no blocking) ----
    def init_touch(self):
        try:
            self.dev = InputDevice(TOUCH_DEV)
            # No set_blocking / set_nonblocking API; we'll use read_one() in poll loop
            caps = self.dev.capabilities().get(ecodes.EV_ABS, [])
            self.use_mt = any(code in (ecodes.ABS_MT_POSITION_X, ecodes.ABS_MT_POSITION_Y)
                              for code, _ in caps)
            print(f"Touch device: {self.dev.name} | use_mt={self.use_mt}")
        except FileNotFoundError:
            print("Touchscreen device not found.")
            self.dev = None

    def poll_touch(self):
        """Poll the touch device with read_one(); process complete frames on SYN."""
        if self.dev is not None:
            try:
                while True:
                    ev = self.dev.read_one()
                    if ev is None:
                        break  # nothing more right now

                    # Prefer BTN_TOUCH to gate, but also support MT tracking ID
                    if ev.type == ecodes.EV_KEY and ev.code == ecodes.BTN_TOUCH:
                        self.touch_down = (ev.value == 1)
                        if not self.touch_down:
                            self.x = self.y = None

                    elif ev.type == ecodes.EV_ABS:
                        # Some panels don't emit BTN_TOUCH; use MT tracking to gate
                        if ev.code == ecodes.ABS_MT_TRACKING_ID:
                            if ev.value == -1:
                                self.touch_down = False
                                self.x = self.y = None
                            else:
                                self.touch_down = True
                            continue  # move on to next event

                        if not self.touch_down:
                            continue  # ignore movement unless finger is down

                        if self.use_mt:
                            if ev.code == ecodes.ABS_MT_POSITION_X:
                                self.x = ev.value
                            elif ev.code == ecodes.ABS_MT_POSITION_Y:
                                self.y = ev.value
                        else:
                            if ev.code == ecodes.ABS_X:
                                self.x = ev.value
                            elif ev.code == ecodes.ABS_Y:
                                self.y = ev.value

                    elif ev.type == ecodes.EV_SYN:
                        # Once per frame: draw only when we have both coordinates and a touch down
                        if not self.touch_down or self.x is None or self.y is None:
                            continue

                        # Map raw → grid (round to nearest cell; avoid off-by-one)
                        col = int((self.x / max(1, TOUCH_WIDTH  - 1)) * (GRID_COLS - 1) + 0.5)
                        row = int((self.y / max(1, TOUCH_HEIGHT - 1)) * (GRID_ROWS - 1) + 0.5)
                        col = max(0, min(GRID_COLS - 1, col))
                        row = max(0, min(GRID_ROWS - 1, row))

                        mr, mc = orient(row, col)
                        idx = serpentine_index(mr, mc)

                        # Paint and leave on
                        self.pixels[idx] = self.current_rgb
                        self.pixels.show()

                        # Update GUI cell at GUI coords
                        if (row, col) in self.rects:
                            self.canvas.itemconfig(self.rects[(row, col)], fill=self.current_hex)

                        # Reset for next frame
                        self.x = self.y = None

            except OSError:
                # device might have been disconnected
                pass

        # poll again soon (~120 Hz). Increase to 4ms if you want more responsiveness.
        self.root.after(8, self.poll_touch)


# =========================
# Main
# =========================
if __name__ == "__main__":
    root = tk.Tk()
    # Fullscreen optional—uncomment if you want it
    root.attributes("-fullscreen", True)

    app = LEDTouchGUI(root)
    root.mainloop()