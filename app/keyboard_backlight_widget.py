'''Keyboard Backlight Widget
This widget provides a UI for controlling the keyboard backlight brightness and mode.
'''

import subprocess
import threading
from gi.repository import Gtk, GLib
from app.widget import WidgetTemplate

class KeyboardBacklightWidget(Gtk.Box, WidgetTemplate):
    '''Widget to control keyboard backlight brightness and mode.'''

    def __init__(self, model=None, image_size=(500, 710)):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.model = model
        self.image_size = image_size
        self.data = None

        # Label
        self.label = Gtk.Label(label="Keyboard Backlight")
        self.pack_start(self.label, False, False, 0)

        # Brightness scale
        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_digits(0)
        self.scale.set_size_request(150, -1)
        self.scale.connect("value-changed", self.on_brightness_changed)
        self.pack_start(self.scale, False, False, 0)

        # Value label
        self.value_label = Gtk.Label(label="0%")
        self.pack_start(self.value_label, False, False, 0)

        # Mode button
        self.modes = ["Manual", "Auto", "Responsive", "Breathe"]
        self.current_mode = 0
        self.mode_button = Gtk.Button(label=f"Mode: {self.modes[self.current_mode]}")
        self.mode_button.connect("clicked", self.on_mode_clicked)
        self.pack_start(self.mode_button, False, False, 0)

        self._debounce_id = None
        self._daemon_proc = None

        self.update()
        self.update_visual()
        self._update_scale_from_ectool()

    def _update_scale_from_ectool(self):
        def worker():
            current_value = 0
            try:
                cmd = ["pkexec", "/usr/bin/ectool", "pwmgetkblight"]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=2)
                for line in result.stdout.splitlines():
                    if "Current keyboard backlight percent:" in line:
                        current_value = int(line.split(":")[-1].strip())
                        break
            except Exception as e:
                print("Error getting backlight value:", e)
            GLib.idle_add(self.scale.set_value, current_value)
            GLib.idle_add(self.value_label.set_text, f"{current_value}%")
        threading.Thread(target=worker, daemon=True).start()

    def on_mode_clicked(self, button):
        self.current_mode = (self.current_mode + 1) % len(self.modes)
        button.set_label(f"Mode: {self.modes[self.current_mode]}")
        mode = self.modes[self.current_mode]
        daemon_path = "/usr/bin/keyboard_backlight_daemon.py"
        def is_daemon_running():
            try:
                result = subprocess.run(["pgrep", "-f", "keyboard_backlight_daemon.py"], capture_output=True, text=True, check=False)
                return bool(result.stdout.strip())
            except Exception:
                return False
        if not is_daemon_running():
            try:
                cmd = ["pkexec", "python3", daemon_path]
                self._daemon_proc = subprocess.Popen(cmd)
            except Exception as e:
                print("Failed to start daemon:", e)
        try:
            with open("/tmp/kb_backlight_mode", "w", encoding="utf-8") as f:
                f.write(mode.lower())
        except OSError as e:
            print("Failed to send mode to daemon:", e)
        self.update()
        self.update_visual()

    def on_brightness_changed(self, scale):
        value = int(scale.get_value())
        self.value_label.set_text(f"{value}%")
        if self.modes[self.current_mode] != "Manual":
            self.current_mode = 0
            self.mode_button.set_label(f"Mode: {self.modes[self.current_mode]}")
        try:
            with open("/tmp/kb_backlight_mode", "w", encoding="utf-8") as f:
                f.write("manual")
        except OSError as e:
            print("Failed to send mode to daemon:", e)
        if self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(100, self._set_brightness, value)
        self.update()
        self.update_visual()

    def _set_brightness(self, value):
        def worker():
            try:
                cmd = ["pkexec", "/usr/bin/ectool", "pwmsetkblight", str(value)]
                subprocess.run(cmd, check=True, timeout=2)
            except Exception as e:
                print("Error setting backlight:", e)
            GLib.idle_add(self._clear_debounce)
        threading.Thread(target=worker, daemon=True).start()
        return False

    def _clear_debounce(self):
        self._debounce_id = None

    def update(self):
        # Set data for UI overlays, if needed
        self.data = {
            "brightness": int(self.scale.get_value()),
            "mode": self.modes[self.current_mode],
            "image_size": self.image_size,
            # "overlays": []
        }

    def update_visual(self):
        # Update label with current brightness and mode
        if self.data:
            self.label.set_text(f"Keyboard Backlight\nBrightness: {self.data['brightness']}%\nMode: {self.data['mode']}")
        else:
            self.label.set_text("Keyboard Backlight\nNo data yet.")
