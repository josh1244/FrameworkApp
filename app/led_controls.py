'''led_controls.py
This module defines the LedControlBox widget for controlling the LEDs on the Framework Laptop.
'''

import subprocess
import inspect
from gi.repository import Gtk

# REDO this logic at some point

class LedControlBox(Gtk.Box):
    '''Widget for controlling the LEDs on the Framework Laptop.'''

    def __init__(self, led_name, on_mode_changed=None, on_color_clicked=None):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        if on_mode_changed is None:
            on_mode_changed = default_on_led_mode_changed
        if on_color_clicked is None:
            on_color_clicked = default_on_led_color_clicked
        self.led_name = led_name
        self.led_state = "Auto"
        self.on_mode_changed = on_mode_changed
        self.on_color_clicked = on_color_clicked

        label_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        led_label = Gtk.Label(label=f"{led_name} LED:")
        led_label.set_halign(Gtk.Align.CENTER)
        self.state_label = Gtk.Label(label=self.led_state)
        self.state_label.set_halign(Gtk.Align.START)
        label_hbox.pack_start(led_label, False, False, 0)
        label_hbox.pack_start(self.state_label, False, False, 0)
        self.pack_start(label_hbox, False, False, 0)

        # On/Off/Auto Button
        mode_labels = ["On", "Auto", "Off"]

        mode_btn = Gtk.Button()
        mode_btn.mode_labels = mode_labels
        mode_btn.current_mode = 1  # Default to Auto
        self.mode_btn = mode_btn
        self.color_btns = {}  # Initialize before _update_mode_btn
        mode_btn.connect("clicked", self._on_mode_btn_clicked)
        self._update_mode_btn(mode_btn)
        self.pack_start(mode_btn, False, False, 0)

        # Color Buttons in 2x3 Grid
        color_names = [
            ("Red", "red"),
            ("Amber", "amber"),
            ("Yellow", "yellow"),
            ("White", "white"),
            ("Green", "green"),
            ("Blue", "blue")
        ]

         # Disable the blue button if led_name is 'power'
        if self.led_name.lower() == "power":
            color_names.remove(("Blue", "blue"))

        color_grid = Gtk.Grid()
        color_grid.set_row_spacing(2)
        color_grid.set_column_spacing(2)
        self.color_btns = {}
        for idx, (color_label, color_value) in enumerate(color_names):
            btn = Gtk.Button(label=color_label)
            self.color_btns[color_value] = btn
            def on_color_btn_clicked(b, color_value=color_value):
                self.mode_btn.current_mode = 0  # 0 is 'On'
                self._update_mode_btn(self.mode_btn)
                self.led_state = color_value
                self.state_label.set_text(color_value.capitalize())
                self._set_selected_color_btn(color_value)
                # Call with overlay if supported
                args = [b, self.led_name.lower(), color_value]
                if len(inspect.signature(self.on_color_clicked).parameters) > 3:
                    args.append(self.get_overlay())
                self.on_color_clicked(*args)
            btn.connect("clicked", on_color_btn_clicked)
            row = idx // 3
            col = idx % 3
            color_grid.attach(btn, col, row, 1, 1)
        self.pack_start(color_grid, False, False, 0)

    def _update_mode_btn(self, btn):
        label = btn.mode_labels[btn.current_mode]
        btn.set_label(label)
        if label == "On":
            # Only set to white if previous state was auto or off
            if self.led_state.lower() in ("auto", "off"):
                self.state_label.set_text("White")
                self.led_state = "white"
                self._set_selected_color_btn("white")
                white_btn = self.color_btns.get("white")
                if white_btn:
                    self.on_color_clicked(white_btn, self.led_name.lower(), "white")
            else:
                # Keep the current color and highlight the button
                self.state_label.set_text(self.led_state.capitalize())
                self._set_selected_color_btn(self.led_state)
        else:
            self.state_label.set_text(label)
            self._set_selected_color_btn(None)

    def _on_mode_btn_clicked(self, btn):
        btn.current_mode = (btn.current_mode + 1) % len(btn.mode_labels)
        self._clear_color_btns()
        self._update_mode_btn(btn)
        state = btn.mode_labels[btn.current_mode]
        if state == "On":
            self.led_state = "white"
        else:
            self.led_state = state
        args = [btn, self.led_name.lower()]
        if len(inspect.signature(self.on_mode_changed).parameters) > 2:
            args.append(self.get_overlay())
        self.on_mode_changed(*args)

    def _set_selected_color_btn(self, selected_color):
        for val, btn in self.color_btns.items():
            if val == selected_color:
                btn.get_style_context().add_class("suggested-action")
            else:
                btn.get_style_context().remove_class("suggested-action")

    def _clear_color_btns(self):
        for btn in self.color_btns.values():
            btn.get_style_context().remove_class("suggested-action")

    def get_overlay(self):
        '''Add an overlay for this LED.'''

        # Map led_name to overlay image filename
        overlay_map = {
            "left": "overlays/framework-left-led-{overlay_id}.png",
            "power": "overlays/framework-power-led-{overlay_id}.png",
            "right": "overlays/framework-right-led-{overlay_id}.png"
        }
        img_name = overlay_map.get(self.led_name.lower())
        # Map color names to RGB values (customize as needed)
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
        color = color_map.get(self.led_state.lower(), (255, 255, 255, 255))
        if img_name and self.led_state.lower() != "off":
            return {"name": img_name, "color": color}
        return None


def default_on_led_mode_changed(button, led_name):
    '''Default handler for LED mode button click.'''
    label = button.get_label().lower()
    if label == "on":
        # The app clicks the white button when switching to "On"
        return
    cmd = ["pkexec", "/usr/bin/ectool", "led", led_name, label]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=False)


def default_on_led_color_clicked(_button, led_name, color=None):
    '''Default handler for LED color button click.'''
    if color:
        cmd = ["pkexec", "/usr/bin/ectool", "led", led_name, color]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd, check=False)
    else:
        print(f"{led_name} LED custom color button clicked")
