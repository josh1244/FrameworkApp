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
- - [X] Support tuned (Fedoras default as of 41)
- - [ ] Support ppd
- [ ] System notifications for hardware events
- [ ] Multi-model support and detection
- [ ] Updates?


- [X] Detects Model
- [X] ectool Installer
- [ ] Interactive Computer Image
- [ ] LED controls
- - [X] Control left, right, power LEDS
- - [X] On/Off/Auto
- - [X] Colors
- - [ ] Brightness of power button
- - [ ] Persitent across reboot?
- - [ ] Get current state and show that for auto
- - [ ] Show the LEDs on the computer image
- - [ ] Should detect the state, on, off, auto, when the app loads and set the button 
- [ ] Battery
- - [X] Charge Percentage
- - [X] Charge State
- - [X] Health
- - [ ] Display on image
- [ ] Ports
- - [ ] Which port is connected to power
- - [X] Which ports are connected to laptop
- - [ ] Which ports are in use
- - [ ] Power draw?
- - [X] Images
- [ ] Show webcam/mic status
- - [ ] Display on image
- [ ] Keyboard
- - [ ] Backlight controls
- - [ ] Autobrightness
- [ ] LED and keyboard Scripts
- [ ] Sleep Mode
- - [ ] Display current mode
- - [ ] Toggle Mode


## Requirements
- Python 3.7+
- GTK 3 (PyGObject)
- Framework laptop (for full feature support)

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
*Made with Python and GTK3.*
