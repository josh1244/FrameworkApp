'''
ExpansionCardsWidget
This widget displays the expansion cards and laptop image, updating periodically.
It is a Gtk.Box and implements the WidgetTemplate interface for integration with the UI.
'''

import subprocess
import re
from gi.repository import Gtk, GLib
from app.image_utils import load_scaled_image
from app.helpers import get_asset_path
from app.widget import WidgetTemplate

class ExpansionCardsWidget(Gtk.Box, WidgetTemplate):
    '''Widget to display expansion cards and laptop image, with periodic update.'''

    def __init__(self, ports=4):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        WidgetTemplate.__init__(self)
        self.set_halign(Gtk.Align.CENTER)
        self.ports = ports
        self.expansion_card_map = {
            "HDMI Expansion Card": "expansion_card_hdmi.png",
            "USB-A Expansion Card": "expansion_card_usb_a.png",
            "Storage Expansion Card": "expansion_card_storage.png",
            "Micro SD Expansion Card": "expansion_card_micro_sd.png",
            "USB-C Expansion Card": "expansion_card_usb_c.png",
            "Fingerprint Sensor / Power Button": None,
            "Wireless Card": None,
        }
        self.result = ["expansion_card_usb_c.png"] * self.ports
        self.left_ports_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.right_ports_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.center_space = Gtk.Box()  # Empty space for image
        self.center_space.set_halign(Gtk.Align.CENTER)
        self._build_ui()
        self.data = None
        
        # Initialize the widget with the current expansion cards
        self.update()
        self.update_visual()

    def _build_ui(self):
        self.left_ports_vbox.set_halign(Gtk.Align.CENTER)
        self.left_ports_vbox.set_valign(Gtk.Align.CENTER)
        # self.left_ports_vbox.set_margin_bottom(50)

        self.right_ports_vbox.set_halign(Gtk.Align.CENTER)
        self.right_ports_vbox.set_valign(Gtk.Align.CENTER)
        # self.right_ports_vbox.set_margin_bottom(50)

        Gtk.Box.pack_start(self, self.left_ports_vbox, False, False, 0)
        Gtk.Box.pack_start(self, self.center_space, False, False, 0)
        Gtk.Box.pack_start(self, self.right_ports_vbox, False, False, 0)

    def _periodic_update(self):
        self.update()
        return True

    def update(self):
        '''Update the detected expansion cards.'''
        result = ["expansion_card_usb_c.png"] * self.ports
        try:
            lsusb = subprocess.run(["lsusb"], capture_output=True, text=True, check=True)
            lsusb_t = subprocess.run(["lsusb", "-t"], capture_output=True, text=True, check=True)
            port_map = {
                "001": 1, # Top right port
                "002": 2, 
                "003": 3, # Bottom left/right port
                "004": 2,
                "005": 2,
                "006": 0, # Top left port
                }
            dev_to_port = {}
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
            for line in lsusb.stdout.splitlines():
                parts = line.strip().split()
                label_line = line.strip()
                extra_label = None
                port_idx = None
                if len(parts) >= 6:
                    bus = parts[1]
                    dev = parts[3][:-1]
                    port = dev_to_port.get((bus, dev))
                    port_idx = port_map.get(port) if port else None
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
                    if extra_label and port_idx is not None and 0 <= port_idx:
                        if port_idx >= self.ports:
                            for i in range(self.ports):
                                if result[i] == "expansion_card_usb_c.png":
                                    result[i] = self.expansion_card_map[extra_label]
                                    break
                        else:
                            result[port_idx] = self.expansion_card_map[extra_label]
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"Error occurred while getting connected expansion cards: {e}")
        self.result = result
        self.data = {"expansion_cards": result}
        self.update_visual()

    def update_visual(self):
        '''Update UI'''
        result = self.result
        for child in list(Gtk.Box.get_children(self.left_ports_vbox)):
            self.left_ports_vbox.remove(child)
        for child in list(Gtk.Box.get_children(self.right_ports_vbox)):
            self.right_ports_vbox.remove(child)
        port_img_size = 160 # 640 / self.ports if self.ports > 0 else 80
        for i, img_name in enumerate(result):
            if i % 2 == 0:
                if img_name:
                    img_path = get_asset_path(img_name)
                    port_img = load_scaled_image(img_path, port_img_size)
                    if port_img:
                        Gtk.Box.pack_start(self.left_ports_vbox, port_img, False, False, 0)
        for i, img_name in enumerate(result):
            if i % 2 == 1:
                if img_name:
                    img_path = get_asset_path(img_name)
                    port_img = load_scaled_image(img_path, port_img_size)
                    if port_img:
                        Gtk.Box.pack_start(self.right_ports_vbox, port_img, False, False, 0)
        Gtk.Widget.show_all(self.left_ports_vbox)
        Gtk.Widget.show_all(self.right_ports_vbox)
        Gtk.Widget.show_all(self.center_space)
