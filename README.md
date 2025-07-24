# Framework Laptop Control

A GTK-based desktop application for controlling and monitoring Framework Laptop features, including model information, images, and various hardware controls.

## Features
- Displays Framework logo and laptop model image
- Shows model name and key hardware features
- Designed with a modern, clean UI using custom fonts
- Modular code structure for easy extension

## Features TODO

- [ ] LED color and brightness controls
- [ ] Fan speed monitoring and control
- [ ] Battery health and charge limit settings
- [ ] Power profile switching
- [ ] Plugged in/on battery status display
- [ ] Sleep type selection
- [ ] System notifications for hardware events
- [ ] Multi-model support and detection
- [ ] Updates?
- [ ] graceful exit of app

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
