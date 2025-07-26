# Framework Laptop Control

A GTK-based desktop application for controlling and monitoring Framework Laptop features, including model information, images, and various hardware controls.

## Features

- Displays Framework logo and laptop model image
- Shows model name and key hardware features
- Designed with a modern, clean UI using custom fonts
- Modular code structure for easy extension

## Features TODO

- [ ] Fan speed monitoring and control
- [ ] Battery health and charge limit settings
- [ ] Power profile switching
- - [x] Support tuned (Fedoras default as of 41)
- - [ ] Support ppd
- [ ] System notifications for hardware events
- [ ] Multi-model support and detection
- [ ] Updates?

- [x] Detects Model
- [x] ectool Installer
- [ ] Interactive Computer Image
- [ ] LED controls
- - [x] Control left, right, power LEDS
- - [x] On/Off/Auto
- - [x] Colors
- - [ ] Brightness of power button
- - [ ] Persitent across reboot?
- - [ ] Get current state and show that for auto
- - [x] Show the LEDs on the computer image
- - [ ] Should detect the state, on, off, auto, when the app loads and set the button
- [ ] Battery
- - [x] Charge Percentage
- - [x] Charge State
- - [x] Health
- - [ ] Display on image
- [ ] Ports
- - [ ] Which port is connected to power
- - [x] Which ports are connected to laptop
- - [ ] Which ports are in use
- - [ ] Power draw?
- - [x] Images
- [ ] Show webcam/mic status
- - [ ] Display on image
- [ ] Keyboard
- - [x] Backlight controls
- - [ ] Autobrightness
- - [x] Patterns
- [ ] LED and keyboard Scripts
- [ ] Sleep Mode
- - [ ] Display current mode
- - [ ] Toggle Mode
- [ ] Show OS on display on image
- - [ ] Brightness should change it
- [ ] App is very slow now with image updating. I need to redo the architecture, so there is a single update loop with variable update timer. It needs to be more modular and less spaghetti

## Requirements

- Python 3.7+
- GTK 3 (PyGObject)
- Framework laptop (for full feature support)

## Additional Requirements

To use the keyboard backlight daemon with keypress detection, you need:

- Python 3.13
- Python development headers (Linux package: `python3.13-dev` or `python3.13-devel`)
- [evdev](https://pypi.org/project/evdev/) Python library
  - Install with: `pip install evdev; pip3 install evdev`

Other dependencies:

- GTK 3 and PyGObject for the UI
- ectool (Framework laptop utility)

## Installation

1. **Install dependencies:**
   - On Ubuntu/Debian:
     ```sh
     sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
     ```
   - On Fedora:
     ```sh
     sudo dnf install python3-gobject gtk3
     ```
   - Install Python packages (if needed):
     ```sh
     pip install PyGObject
     ```
2. **Clone this repository:**
   ```sh
   git clone <repo-url>
   cd FrameworkApp
   ```
3. **(Optional) Install Graphik font:**
   - Copy the `fonts/` directory contents to your system fonts folder or use a font manager.

## Install

Install ectool with:

```sh
bash ./install.sh
```

## Usage

Run the application with:

```sh
python3 main.py
```

## Project Structure

- `main.py` — Entry point for the application
- `ui.py` — Main GTK window and UI logic
- `framework_model.py` — Model information and data
- `image_utils.py` — Image loading and scaling utilities
- `assets/` — Images and icons
- `fonts/` — Custom fonts (Graphik)

## Customization

- Add new laptop models or images by editing `framework_model.py` and placing images in `assets/`.
- Update the UI or add new controls in `ui.py`.

## License

This project is not affiliated with Framework Computer, Inc. All trademarks are property of their respective owners.

---

_Made with Python and GTK3._
