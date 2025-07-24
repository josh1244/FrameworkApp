"""
power_status.py
Reads battery percentage, charging status, and health for Framework laptop.
"""

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

def read_file(path):
    '''Reads the content of a file and returns it as a string.'''
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except (OSError, IOError):
        return None

def get_power_path(filename, battery_name='BAT1'):
    '''Returns the path to the specified battery sysfs file.'''
    return os.path.join(f'/sys/class/power_supply/{battery_name}', filename)


def get_battery_stats(battery_name='BAT1'):
    '''Returns a dictionary with battery stats: percentage, status, and health.'''

    percent = read_file(get_power_path('capacity', battery_name))
    status = read_file(get_power_path('status', battery_name))
    charge_full = read_file(get_power_path('charge_full', battery_name))
    charge_full_design = read_file(get_power_path('charge_full_design', battery_name))
    health = None
    if charge_full and charge_full_design:
        try:
            health = int(charge_full) * 100 // int(charge_full_design)
        except (ValueError, ZeroDivisionError):
            health = None
    return {
        'percentage': percent,
        'status': status,
        'health': health
    }


class PowerStatusBox(Gtk.Box):
    '''Widget for displaying battery status and health information.'''

    def __init__(self, battery_name='BAT1', update_interval_ms=5000):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.battery_name = battery_name
        self.battery_label = Gtk.Label(xalign=0)
        self.battery_label.set_justify(Gtk.Justification.LEFT)
        self.battery_label.set_halign(Gtk.Align.START)
        self.pack_start(self.battery_label, True, True, 0)
        self.update()
        # Set up periodic update
        GLib.timeout_add(update_interval_ms, self._periodic_update)

    def _periodic_update(self):
        self.update()
        return True  # Continue calling

    def update(self):
        '''Update the battery status display.'''

        battery = get_battery_stats(self.battery_name)
        battery_lines = [
            f"Battery Percentage: {battery['percentage']}%" if battery['percentage'] is not None else "Battery Percentage: Unknown",
            f"Charging Status: {battery['status']}" if battery['status'] is not None else "Charging Status: Unknown",
            f"Battery Health: {battery['health']}%" if battery['health'] is not None else "Battery Health: Unknown"
        ]
        self.battery_label.set_text("\n".join(battery_lines))

    def set_battery_name(self, battery_name):
        '''Set a new battery name and update the display.'''
        
        self.battery_name = battery_name
        self.update()
