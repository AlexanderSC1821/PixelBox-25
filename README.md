Pixelbox Setup Guide

A simple guide for preparing a brand-new Raspberry Pi to run the Pixelbox project. This walkthrough covers cloning the repo, installing dependencies, wiring the hardware, and launching Pixelbox.

⸻

1. Requirements

Hardware
	•	Raspberry Pi 4B or Pi Zero 2 W
	•	WS2812B 16×16 LED Matrix (256 pixels)
	•	USB capacitive touchscreen overlay
	•	5V power supply (3A minimum, separate LED PSU recommended)
	•	Jumper wires
	•	Access to the Pi GPIO header (GPIO12 recommended for LED data)

Software
	•	Raspberry Pi OS (Bookworm recommended)
	•	Python 3
	•	Git

2. First-Time Pi Setup

Update the system:
sudo apt update && sudo apt upgrade -y

Enable interfaces:
sudo raspi-config

Then navigate to:
Interface Options → enable SPI and I2C (optional)



3. Clone the Pixelbox Repository

Choose a directory (recommended: home folder):
cd ~
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

4. Install Python Dependencies

Install required packages:
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel evdev

Install Blinka for GPIO access:
sudo pip3 install adafruit-blinka

5. Hardware Wiring Guide
Function	LED Matrix	Raspberry Pi Pin
DATA IN	Din	GPIO12 (Pin 32)
5V	5V	Pin 4 or dedicated 5V PSU
GND	GND	Pin 6 (must match Pi ground)

Important: If using an external 5V supply, always connect the ground of the LED supply to the ground of the Pi.

Touchscreen

USB capacitive overlays require no drivers.
Plug in the USB cable and confirm detection:
ls /dev/input

6. Running Pixelbox for the First Time

Test touchscreen input:
sudo evtest

Run the Pixelbox software:
python3 touchToLED.py

If scrollingText.py exists in the same folder, Pixelbox will automatically start the scrolling text feature on launch.
7. Using Pixelbox

Touch Interaction
	•	Touch coordinates are mapped to the 16×16 LED matrix.
	•	Drawing and erasing modes are supported depending on your version of the code.
	•	Orientation toggles and developer features are also available if enabled.

Scrolling Text
	•	Automatically starts if scrollingText.py is present.
	•	Customize text inside that file.
	•	Disable startup by commenting out the import inside touchToLED.py.

⸻

8. Updating Pixelbox
To pull new changes:
cd <your-repo>
git pull

9. Troubleshooting

LEDs not lighting up
	•	Confirm the data pin matches code:
PIXEL_PIN = board.D12
Ensure ground is shared across Pi and LED power supply.
	•	Try lowering brightness:
BRIGHTNESS = 0.1

Touchscreen not recognized

Check available input devices:
ls /dev/input
sudo evtest

Missing module errors

Reinstall dependencies:
sudo pip3 install adafruit-blinka rpi_ws281x adafruit-circuitpython-neopixel evdev

10. Suggested Project Structure
Pixelbox/
│── touchToLED.py
│── scrollingText.py
│── images/
│── utils/
│── README.md

