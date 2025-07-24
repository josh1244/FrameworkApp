# Keyboard Backlight Control Documentation

This document describes the implementation and usage of the keyboard backlight control in the FrameworkApp.

## Overview
The keyboard backlight control allows users to adjust the brightness and select different lighting modes for the keyboard. It communicates with a background daemon to apply changes and supports several modes:
- Manual
- Auto
- Breathe
- Responsive

## UI Widget (`KeyboardBacklightBox`)
- Built with GTK.
- Provides a slider to set brightness (0-100%).
- Shows the current brightness value.
- Includes a button to cycle through modes (Manual, Auto, Breathe, Responsive).

### Brightness Slider
- When the slider is moved, the mode is set to Manual.
- The brightness value is sent to the daemon using `ectool`.
- The daemon is notified of the mode change by writing "manual" to `/tmp/kb_backlight_mode`.

### Mode Button
- Cycles through available modes.
- When a mode is selected, its name is written to `/tmp/kb_backlight_mode` (in lowercase).
- If the daemon is not running, it is started automatically.

## Daemon Communication
- The daemon reads `/tmp/kb_backlight_mode` to determine the current mode.
- Supported modes trigger different lighting patterns or behaviors.
- Brightness changes are applied using `ectool` via `pkexec` for elevated permissions.


## How Changing Daemon Mode Works
The UI writes the selected mode (e.g., "manual", "auto", "breathe", "responsive") to the file `/tmp/kb_backlight_mode`. The daemon continuously reads this file to check for mode changes. When a new mode is detected, the daemon immediately stops the currently running pattern thread and starts a new thread for the selected mode.

This means pattern changes (including breathe, auto, and responsive) now take effect instantly, even if the pattern is in a sleep loop or waiting for input. The daemon uses a `stop_pattern` flag to signal the running pattern thread to exit, ensuring smooth and responsive mode switching.

### Responsive Pattern Details
- Uses `evdev` to listen for keypress events from the keyboard input device.
- When a key is pressed, the backlight turns on and a timer is reset.
- If no key is pressed for the timeout duration, the backlight turns off.
- The pattern thread is stopped if the mode changes, so the daemon can switch to another pattern instantly.

## Example Code Snippet
```python
# Notify daemon of manual mode when slider is used
try:
    with open("/tmp/kb_backlight_mode", "w", encoding="utf-8") as f:
        f.write("manual")
except OSError as e:
    print("Failed to send mode to daemon:", e)
```

## Troubleshooting
- Ensure `ectool` is installed and accessible at `/usr/bin/ectool`.
- The daemon requires root privileges; `pkexec` is used for this purpose.
- If the daemon does not respond, check that `/tmp/kb_backlight_mode` is being updated and the daemon process is running.

## File Locations
- UI code: `app/keyboard_backlight.py`
- Daemon: `app/tools/keyboard_backlight_daemon.py`
- IPC file: `/tmp/kb_backlight_mode`

## References
- See `LED_CONTROL.md` for related hardware control details.
