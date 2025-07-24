'''led_controls.py
This module defines the LedControlBox widget for controlling the LEDs on the Framework Laptop.
'''

import os
import subprocess

# REDO this logic at some point

import gi
from gi.repository import Gtk

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
        mode_labels = ["On", "Off", "Auto"]

        mode_btn = Gtk.Button()
        mode_btn.mode_labels = mode_labels
        mode_btn.current_mode = 2  # Default to Auto
        self.mode_btn = mode_btn
        self.color_btns = {}  # Initialize before _update_mode_btn
        mode_btn.connect("clicked", self._on_mode_btn_clicked)
        self._update_mode_btn(mode_btn)
        self.pack_start(mode_btn, False, False, 0)

        # Color Buttons in 2x3 Grid
        color_names = [
            ("Red", "red"),
            ("Green", "green"),
            ("Blue", "blue"),
            ("Yellow", "yellow"),
            ("White", "white"),
            ("Amber", "amber")
        ]
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
                self.on_color_clicked(b, self.led_name.lower(), color_value)
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
        self.on_mode_changed(btn, self.led_name.lower())

    def _set_selected_color_btn(self, selected_color):
        for val, btn in self.color_btns.items():
            if val == selected_color:
                btn.get_style_context().add_class("suggested-action")
            else:
                btn.get_style_context().remove_class("suggested-action")

    def _clear_color_btns(self):
        for btn in self.color_btns.values():
            btn.get_style_context().remove_class("suggested-action")


def default_on_led_mode_changed(button, led_name):
    '''Default handler for LED mode button click.'''
    label = button.get_label().lower()
    cmd = ["pkexec", "/usr/bin/ectool", "led", led_name, label]
    print("Running:", " ".join(cmd))
    subprocess.run(cmd)


def default_on_led_color_clicked(_button, led_name, color=None):
    '''Default handler for LED color button click.'''
    if color:
        cmd = ["pkexec", "/usr/bin/ectool", "led", led_name, color]
        print("Running:", " ".join(cmd))
        subprocess.run(cmd)
    else:
        print(f"{led_name} LED custom color button clicked")
