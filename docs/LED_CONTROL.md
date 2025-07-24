
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
