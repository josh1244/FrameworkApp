
# Keyboard Backlight Control

The keyboard backlight brightness can be controlled via the Linux sysfs interface:

```sh
echo <value> | sudo tee /sys/class/leds/chromeos::kbd_backlight/brightness
```

- `<value>` is an integer from **0** (off) to **100** (maximum brightness).
- You must have root privileges to write to this file (use `sudo`).

## Example

Set keyboard backlight to 50% brightness:

```sh
echo 50 | sudo tee /sys/class/leds/chromeos::kbd_backlight/brightness
```

Set keyboard backlight off:

```sh
echo 0 | sudo tee /sys/class/leds/chromeos::kbd_backlight/brightness
```

## Notes
- This method works on Framework laptops (and other devices) that expose the keyboard backlight via `/sys/class/leds/chromeos::kbd_backlight/`.
- The value range may vary on some systems; check the contents of `/sys/class/leds/chromeos::kbd_backlight/max_brightness` for the maximum allowed value.



## ectool LED Command Logic

The `cmd_led` function in ectool is responsible for controlling the various LEDs on Framework laptops. Here is how it works:

**Usage:**

```
ectool led <name> <query | auto | off | <color> | <color>=<value>...>
```

- `<name>`: The LED to control (e.g., `left`, `right`, `power`, `battery`, etc.).
- The second argument can be:
  - `query`: Query the supported brightness range for each color of the specified LED.
  - `auto`: Set the LED to automatic control mode.
  - `off`: Turn the LED off (all colors set to 0).
  - `<color>`: Set the specified color to maximum brightness (e.g., `red`).
  - `<color>=<value>`: Set the specified color to a specific brightness value (e.g., `red=128`). Multiple color assignments can be provided.

**How it works:**

1. The function checks that at least three arguments are provided (command, LED name, and action).
2. It validates the LED name using `find_led_id_by_name`. If invalid, it prints valid names and exits.
3. If the action is `query`, it sends a query command to the EC (Embedded Controller) and prints the brightness range for each color.
4. If the action is `off`, all brightness values are set to 0 (LED off).
5. If the action is `auto`, the LED is set to automatic mode.
6. If a color name is provided, that color is set to maximum brightness.
7. If color assignments are provided (e.g., `red=128`), it parses each and sets the specified brightness for each color.
8. The command is sent to the EC, and the result is returned.

**Supported colors:** `red`, `green`, `blue`, `yellow`, `white`, `amber`

**Supported LEDs:** `power`, `left`, `right`,

**Example commands:**

```
sudo ./ectool led left red
sudo ./ectool led power auto
sudo ./ectool led right off
sudo ./ectool led left query
```


## Features for app
Control left, right, power LEDS
On/Off/Auto
Colors
Persitent across reboot?

Laptop image with the LEDS that actually change color!
Get current state and show that for auto
Show the leds on the laptop image
show webcam/mic status
power button backlight

Should detect the state, on, off, auto, when the app loads and set the button toggles correctly