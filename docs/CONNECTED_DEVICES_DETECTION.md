# FrameworkApp Connected Devices Detection

This document describes the logic and heuristics used by the `ConnectedDevicesBox` widget in the FrameworkApp to detect and label connected devices on Framework laptops.

## Overview

The `ConnectedDevicesBox` widget periodically runs `lsusb` and `lsusb -t` to detect connected USB devices and expansion cards. It then applies a set of heuristics to label and display only the most relevant devices, such as expansion cards, fingerprint sensor, and wireless card.

## Port Mapping

Framework laptops have specific USB-C ports, which are mapped to friendly names:

| Port Number | Friendly Name    |
|-------------|------------------|
| 001         | Top Right        |
| 002         | Bottom Right     |
| 003         | Bottom Left/Right|
| 004         | Top/Bottom Left  |
| 006         | Top Left         |
| 009, 010    | Internal         |

The code parses the output of `lsusb -t` to map device numbers to these port numbers.

## Device Labeling Heuristics

For each device found by `lsusb`, the following heuristics are applied to assign a human-friendly label (`extra_label`). Only devices with an `extra_label` are shown in the UI.

- **HDMI Expansion Card**: If the device name contains `HDMI` or matches Framework's HDMI expansion card signature.
- **USB-A Expansion Card**: If the device name contains `USB3.0`, `USB2.0`, `USB-A`, or matches Framework's USB-A expansion card signature.
- **Storage Expansion Card**: If the device name contains `13fe:6500` or `USB DISK 3.2`.
- **Micro SD Expansion Card**: If the device name contains `090c:3350` or `USB DISK`.
- **Fingerprint Sensor / Power Button**: If the device name contains `27c6:609c` or both `GOODIX` and `FINGERPRINT`.
- **Wireless Card**: If the device name contains `8087:0032` or both `INTEL` and `BLUETOOTH`.

If a device is associated with a known port, the port label is appended in brackets (e.g., `HDMI Expansion Card [Top Right]`).

## Example Output

```
HDMI Expansion Card [Top Right]
USB-A Expansion Card [Bottom Right]
Fingerprint Sensor / Power Button [Internal]
Wireless Card [Internal]
```

## Notes
- Only devices with a recognized `extra_label` are shown.
- The full `lsusb` name is not displayed, only the label and port.
- The detection logic can be extended with more heuristics for new expansion cards or devices.
- It is not possible to detect USB-C or USB-A Cards
- It is not certain about the position
- It might be different on other models
- My bottom left port seems to be damaged.

---

For more details, see the implementation in `app/connected_devices.py`.
