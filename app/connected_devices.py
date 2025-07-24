'''Widget to display connected devices (USB-A, USB-C, HDMI, storage, SD, etc).
This widget periodically checks for connected devices using lsblk and lsusb commands.'''

import threading
import subprocess
from gi.repository import Gtk, GLib

class ConnectedDevicesBox(Gtk.Box):
    '''Widget to display connected devices (USB-A, USB-C, HDMI, storage, SD, etc).'''
    def __init__(self, update_interval_ms=5000):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        label = Gtk.Label(label="Connected Devices:", xalign=0)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_halign(Gtk.Align.START)
        self.pack_start(label, False, False, 0)
        self.devices_list = Gtk.Label(label="(Detecting...)", xalign=0)
        self.devices_list.set_justify(Gtk.Justification.LEFT)
        self.devices_list.set_halign(Gtk.Align.START)
        self.pack_start(self.devices_list, False, False, 0)
        self.update_devices()
        GLib.timeout_add(update_interval_ms, self._periodic_update)



    def update_devices(self):
        '''Update the list of connected devices, showing USB topology and sysfs path.'''
        try:
            lsblk = subprocess.run(["lsblk", "-o", "NAME,TYPE,MOUNTPOINT,MODEL,TRAN"], capture_output=True, text=True)
            lsusb = subprocess.run(["lsusb"], capture_output=True, text=True)
            lsusb_t = subprocess.run(["lsusb", "-t"], capture_output=True, text=True)
            devices = []
            # USB devices (USB-A, USB-C, HDMI adapters, etc)
            # Map Port number to friendly name for Framework laptop
            port_map = {
                "001": "Top Right",
                "002": "Bottom Right",
                "003": "Bottom Left/Right",
                "004": "Top/Bottom Left",
                "006": "Top Left",
            }
            # Parse lsusb -t to map Dev to Port
            dev_to_port = {}
            import re
            current_bus = None
            for tline in lsusb_t.stdout.splitlines():
                m = re.match(r"/:  Bus (\d+)\.Port (\d+): Dev (\d+),", tline)
                if m:
                    current_bus = m.group(1)
                m2 = re.match(r"\s*\|__ Port (\d+): Dev (\d+),", tline)
                if m2 and current_bus:
                    port = m2.group(1).zfill(3)
                    devnum = m2.group(2).zfill(3)
                    dev_to_port[(current_bus, devnum)] = port

            port_devices = []
            other_devices = []
            for line in lsusb.stdout.splitlines():
                parts = line.strip().split()
                label_line = line.strip()
                extra_label = None
                has_port_label = False
                if len(parts) >= 6:
                    bus = parts[1]
                    dev = parts[3][:-1]  # Remove trailing ':'
                    sysfs_path = self._find_sysfs_path(bus, dev)
                    port_label = None
                    port = dev_to_port.get((bus, dev))
                    if port:
                        port_label = port_map.get(port, f"Port {port}")
                        has_port_label = True
                    # Heuristic: label HDMI, USB-A, and Micro SD Expansion Card
                    if "HDMI" in label_line.upper():
                        extra_label = "HDMI Expansion Card"
                    elif any(x in label_line.upper() for x in ["USB3.0", "USB2.0", "USB-A"]):
                        extra_label = "USB-A Expansion Card"
                    elif "FRAMEWORK" in label_line.upper() and ("0001" in label_line or "0003" in label_line):
                        extra_label = "USB-A Expansion Card"
                    elif "FRAMEWORK" in label_line.upper() and "0002" in label_line:
                        extra_label = "HDMI Expansion Card"
                    elif "13fe:6500" in label_line or "USB DISK 3.2" in label_line.upper():
                        extra_label = "Storage Expansion Card"
                    elif "090c:3350" in label_line or "USB DISK" in label_line.upper():
                        extra_label = "Micro SD Expansion Card"
                    # You can add more heuristics for other cards
                    if port_label:
                        label_line += f"  [{port_label}]"
                    if extra_label:
                        label_line += f"  <{extra_label}>"
                    entry = f"{label_line}\n  sysfs: {sysfs_path if sysfs_path else '(unknown)'}"
                    if has_port_label:
                        port_devices.append(entry)
                    else:
                        other_devices.append(entry)
                else:
                    other_devices.append(label_line)
            # Show port devices in their own section
            sections = []
            if port_devices:
                sections.append("Devices with Known USB-C Port:")
                sections.extend(port_devices)
            if other_devices:
                sections.append("Other USB Devices:")
                sections.extend(other_devices)
            # Show USB topology tree
            sections.append("\nUSB Topology (lsusb -t):\n" + lsusb_t.stdout.strip())
            if sections:
                self.devices_list.set_text("\n".join(sections))
            else:
                self.devices_list.set_text("No external devices detected.")
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Error detecting devices: {e}")
            self.devices_list.set_text(f"Error detecting devices: {e}")
        return True

    def _find_sysfs_path(self, bus, dev):
        '''Try to find the sysfs path for a given bus/device number.'''
        import os
        # USB devices are in /sys/bus/usb/devices/usbX/Y-Z
        # Try to match bus and device number
        try:
            for entry in os.listdir("/sys/bus/usb/devices"):
                devpath = f"/sys/bus/usb/devices/{entry}"
                busnum_path = os.path.join(devpath, "busnum")
                devnum_path = os.path.join(devpath, "devnum")
                if os.path.exists(busnum_path) and os.path.exists(devnum_path):
                    with open(busnum_path) as fbus, open(devnum_path) as fdev:
                        if fbus.read().strip().zfill(3) == bus and fdev.read().strip().zfill(3) == dev:
                            return devpath
        except Exception:
            pass
        return None
    
    def _periodic_update(self):
        '''Periodically update the device list.'''

        # Run in a thread to avoid blocking GTK
        threading.Thread(target=self.update_devices, daemon=True).start()
        return True