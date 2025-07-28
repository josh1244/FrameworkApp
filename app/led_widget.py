'''LED Control Widget Module
This module defines a widget for controlling the left, power, and right LEDs on the Framework Laptop.
'''

import subprocess
from gi.repository import Gtk
from app.widget import WidgetTemplate

class LedWidget(Gtk.Box, WidgetTemplate):
    '''A widget for controlling the left, power, and right LEDs.'''

    def __init__(self, model=None):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.model = model

        self.leds = {}
        led_names = ["Left", "Power", "Right"]
        for led_name in led_names:
            led_frame = Gtk.Frame(label=f"{led_name} LED")
            led_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
            led_frame.add(led_vbox)


            # Mode button (On/Auto/Off)
            mode_labels = ["On", "Auto", "Off"]
            mode_btn = Gtk.Button(label=mode_labels[1])
            mode_btn.mode_labels = mode_labels
            mode_btn.current_mode = 1  # Default to Auto
            mode_btn.connect("clicked", self._on_mode_btn_clicked, led_name.lower())
            led_vbox.add(mode_btn)

            # Color buttons (2x3 grid)
            color_names = [
                ("Red", "red"),
                ("Amber", "amber"),
                ("Yellow", "yellow"),
                ("White", "white"),
                ("Green", "green"),
                ("Blue", "blue")
            ]
            if led_name.lower() == "power":
                color_names = [c for c in color_names if c[1] != "blue"]
            color_grid = Gtk.Grid()
            color_grid.set_row_spacing(2)
            color_grid.set_column_spacing(2)
            color_btns = {}
            for idx, (color_label, color_value) in enumerate(color_names):
                btn = Gtk.Button(label=color_label)
                color_btns[color_value] = btn
                btn.connect("clicked", self._on_color_btn_clicked, led_name.lower(), color_value, mode_btn)
                row = idx // 3
                col = idx % 3
                color_grid.attach(btn, col, row, 1, 1)
            led_vbox.add(color_grid)

            self.leds[led_name.lower()] = {
                "mode_btn": mode_btn,
                "color_btns": color_btns,
                "current_color": "white",
                "current_mode": "Auto"
            }
            self.add(led_frame)

    def _on_mode_btn_clicked(self, btn, led_name):
        mode_labels = btn.mode_labels
        btn.current_mode = (btn.current_mode + 1) % len(mode_labels)
        label = mode_labels[btn.current_mode]
        btn.set_label(label)
        self.leds[led_name]["current_mode"] = label
        # If On, set to white if coming from auto/off
        if label == "On":
            if self.leds[led_name]["current_color"] in ("auto", "off"):
                color = "white"
            else:
                color = self.leds[led_name]["current_color"]
            # state_label.set_text(color.capitalize())
            self.leds[led_name]["current_color"] = color
            self._set_selected_color_btn(led_name, color)
            self._run_led_command(led_name, color)
        else:
            # state_label.set_text(label)
            self.leds[led_name]["current_color"] = label.lower()
            self._set_selected_color_btn(led_name, None)
            self._run_led_command(led_name, label.lower())

    def _on_color_btn_clicked(self, _btn, led_name, color_value, mode_btn):
        mode_btn.current_mode = 0  # On
        mode_btn.set_label(mode_btn.mode_labels[0])
        self.leds[led_name]["current_color"] = color_value
        self.leds[led_name]["current_mode"] = "On"
        self._set_selected_color_btn(led_name, color_value)
        self._run_led_command(led_name, color_value)

    def _set_selected_color_btn(self, led_name, selected_color):
        for val, btn in self.leds[led_name]["color_btns"].items():
            if val == selected_color:
                btn.get_style_context().add_class("suggested-action")
            else:
                btn.get_style_context().remove_class("suggested-action")

    def _run_led_command(self, led_name, value):
        # Map mode/color to ectool command
        cmd = ["pkexec", "/usr/bin/ectool", "led", led_name, value]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=False)

    def update(self):
        '''Update method called by ui.py'''

        # Set self.data with overlays for the UI
        overlays = self.get_overlays()
        if overlays:
            self.data = {
                "overlays": overlays
            }

    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''
        return

    def get_overlay(self, led_name):
        '''Return overlay dict for the given LED, or None if off.'''

        # Map led_name to overlay image filename
        overlay_map = {
            "left": "overlays/framework-left-led-{overlay_id}.png",
            "power": "overlays/framework-power-led-{overlay_id}.png",
            "right": "overlays/framework-right-led-{overlay_id}.png"
        }
        color_map = {
            "red": (255, 0, 0, 255),
            "amber": (255, 191, 0, 255),
            "yellow": (255, 255, 0, 255),
            "white": (255, 255, 255, 255),
            "green": (0, 255, 0, 255),
            "blue": (0, 0, 255, 255),
            "auto": (0, 0, 0, 0),
            "off": (0, 0, 0, 0)
        }
        led = self.leds.get(led_name)
        if not led:
            return None
        color = led["current_color"].lower()
        if color == "off":
            return None
        img_name = overlay_map.get(led_name)
        color_rgba = color_map.get(color, (255, 255, 255, 255))
        if img_name and color != "off":
            return {"name": led_name, "path": img_name, "color": color_rgba}
        return None

    def get_overlays(self):
        '''Return a list of overlays for all LEDs.'''

        overlays = []
        for led_name in self.leds:
            overlay = self.get_overlay(led_name)
            if overlay:
                overlays.append(overlay)
        return overlays