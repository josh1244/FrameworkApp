'''Sleep Mode Widget for Framework Laptop
This widget allows users to view and change the sleep mode of their Framework Laptop.
'''

import subprocess
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from app.widget import WidgetTemplate


class SleepModeWidget(Gtk.Box, WidgetTemplate):
    '''Widget to manage sleep modes on Framework Laptop'''

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.add(box)

        self.sleep_modes = self.get_available_sleep_modes()
        self.current_mode = None
        self.data = {}

        # GUI elements
        self.label = Gtk.Label(label="Current sleep mode: Unknown")
        box.pack_start(self.label, False, False, 0)

        self.combo = Gtk.ComboBoxText()
        for mode in self.sleep_modes:
            self.combo.append_text(mode)
        box.pack_start(self.combo, False, False, 0)

        self.button = Gtk.Button(label="Set Sleep Mode")
        self.button.connect("clicked", self.on_set_mode_clicked)
        box.pack_start(self.button, False, False, 0)

        self.update()
        self.update_visual()

    def on_set_mode_clicked(self, _):
        '''Handle button click to set sleep mode'''

        new_mode = self.combo.get_active_text()
        if new_mode in self.sleep_modes:
            if self.set_sleep_mode(new_mode):
                self.label.set_text(f"Current sleep mode: {new_mode}")
            else:
                self.label.set_text("Failed to change sleep mode. Try running as root.")
        else:
            self.label.set_text("Invalid mode.")

    def get_available_sleep_modes(self):
        '''Get available sleep modes from the system'''

        # Example: return a list of supported sleep modes
        # This could be customized for your system
        return ['s2idle', 'deep']

    def get_current_sleep_mode(self):
        '''Get the current sleep mode from the system'''

        try:
            with open('/sys/power/mem_sleep', 'r', encoding='utf-8') as f:
                modes = f.read().strip()
            # The current mode is wrapped in brackets, e.g. "s2idle [deep]"
            for mode in self.sleep_modes:
                if f'[{mode}]' in modes:
                    return mode
            return None
        except OSError:
            return None

    def set_sleep_mode(self, mode):
        '''Set the sleep mode on the system'''

        if mode not in self.sleep_modes:
            raise ValueError(f"Invalid sleep mode: {mode}")
        try:
            # Use pkexec to echo the mode into the file with root privileges
            cmd = [
                'pkexec', 'sh', '-c', f'echo {mode} > /sys/power/mem_sleep'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode == 0
        except Exception:
            return False

    def update(self):
        '''Update method called by ui.py'''

        self.current_mode = self.get_current_sleep_mode()
        self.data = {
            'current_mode': self.current_mode,
            'available_modes': self.sleep_modes
        }

    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''
        
        self.current_mode = self.get_current_sleep_mode()
        if self.current_mode:
            self.label.set_text(f"Current sleep mode: {self.current_mode}")
            # Set combo to current mode
            idx = self.sleep_modes.index(self.current_mode) if self.current_mode in self.sleep_modes else 0
            self.combo.set_active(idx)
        else:
            self.label.set_text("Current sleep mode: Unknown")
