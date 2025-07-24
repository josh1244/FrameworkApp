'''Keyboard Backlight Control Widget
This widget allows users to control the keyboard backlight brightness
using a scale widget. It retrieves the current brightness from ectool and updates it on change.
'''

import subprocess
import threading
from gi.repository import Gtk, GLib

class KeyboardBacklightBox(Gtk.Box):
    '''Widget to control keyboard backlight brightness.'''

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.set_border_width(10)

        label = Gtk.Label(label="Keyboard Backlight:")
        self.pack_start(label, False, False, 0)

        # Get current backlight value from ectool (non-blocking)
        self.scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 100, 1)
        self.scale.set_digits(0)
        self.scale.set_size_request(150, -1)
        self.scale.connect("value-changed", self.on_brightness_changed)
        self.pack_start(self.scale, True, True, 0)

        self.value_label = Gtk.Label(label="0%")
        self.pack_start(self.value_label, False, False, 0)

        def update_scale_from_ectool():
            def worker():
                current_value = 0
                try:
                    cmd = ["pkexec", "/usr/bin/ectool", "pwmgetkblight"]
                    print("Running:", " ".join(cmd))
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=2)
                    for line in result.stdout.splitlines():
                        if "Current keyboard backlight percent:" in line:
                            current_value = int(line.split(":")[-1].strip())
                            break
                except subprocess.CalledProcessError as e:
                    print("Subprocess error occurred:", e)
                except ValueError as e:
                    print("Value parsing error occurred:", e)
                except subprocess.TimeoutExpired as e:
                    print("Subprocess timeout:", e)
                GLib.idle_add(self.scale.set_value, current_value)
                GLib.idle_add(self.value_label.set_text, f"{current_value}%")
            threading.Thread(target=worker, daemon=True).start()
        update_scale_from_ectool()

        # Combine auto brightness and pattern selection into one button
        self.modes = ["Manual","Auto", "Responsive", "Breathe"]
        self.current_mode = 0
        self.mode_button = Gtk.Button(label=self.modes[self.current_mode])
        self.mode_button.connect("clicked", self.on_mode_clicked)
        self.pack_start(self.mode_button, False, False, 0)

        # Initialize debounce id attribute
        self._debounce_id = None

        # Track daemon process
        self._daemon_proc = None

    def on_mode_clicked(self, button):
        '''Callback for mode button click to cycle through modes.'''

        self.current_mode = (self.current_mode + 1) % len(self.modes)
        button.set_label(f"Mode: {self.modes[self.current_mode]}")
        ctx = button.get_style_context()
        mode = self.modes[self.current_mode]

        # Handle daemon process for all modes
        daemon_path = "/usr/bin/keyboard_backlight_daemon.py"
        # Check if daemon is already running
        def is_daemon_running():
            try:
                result = subprocess.run(["pgrep", "-f", "keyboard_backlight_daemon.py"], capture_output=True, text=True, check=False)
                return bool(result.stdout.strip())
            except subprocess.SubprocessError:
                return False

        if not is_daemon_running():
            print("Starting keyboard backlight daemon...")
            try:
                cmd = ["pkexec", "python3", daemon_path]
                print("Running:", " ".join(cmd))
                self._daemon_proc = subprocess.Popen(cmd)
            except subprocess.SubprocessError as e:
                print("Failed to start daemon:", e)
        else:
            print("Daemon already running.")
        # Send mode to daemon (simple IPC: write to a file)
        try:
            with open("/tmp/kb_backlight_mode", "w", encoding="utf-8") as f:
                f.write(mode.lower())
        except OSError as e:
            print("Failed to send mode to daemon:", e)

    def on_brightness_changed(self, scale):
        '''Callback for when the brightness scale is changed.'''

        value = int(scale.get_value())
        self.value_label.set_text(f"{value}%")

        # Set mode to Manual if not already
        if self.modes[self.current_mode] != "Manual":
            self.current_mode = 0
            self.mode_button.set_label(f"Mode: {self.modes[self.current_mode]}")
            ctx = self.mode_button.get_style_context()
            ctx.remove_class("suggested-action")
        # Notify daemon of manual mode
        try:
            with open("/tmp/kb_backlight_mode", "w", encoding="utf-8") as f:
                f.write("manual")
        except OSError as e:
            print("Failed to send mode to daemon:", e)

        # Debounce: only run ectool after 100ms of no slider movement
        if hasattr(self, '_debounce_id') and self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(100, self._set_brightness, value)

    def _set_brightness(self, value):
        '''Set the keyboard backlight brightness using ectool (non-blocking).'''
        def worker():
            try:
                cmd = ["pkexec", "/usr/bin/ectool", "pwmsetkblight", str(value)]
                print("Running:", " ".join(cmd))
                subprocess.run(cmd, check=True, timeout=2)
            except subprocess.CalledProcessError as e:
                print("Subprocess error occurred:", e)
            except subprocess.TimeoutExpired as e:
                print("Subprocess timeout:", e)
            except OSError as e:
                print("OS error occurred:", e)
            GLib.idle_add(self._clear_debounce)
        threading.Thread(target=worker, daemon=True).start()
        return False  # Only run once

    def _clear_debounce(self):
        self._debounce_id = None
