'''Power Status Widget Module
This module defines a widget for displaying battery status and health.
It inherits from Gtk.Box and implements the WidgetTemplate interface.
'''

import os
from PIL import Image, ImageDraw, ImageFont
from gi.repository import Gtk, GLib
from app.widget import WidgetTemplate

class PowerStatusWidget(Gtk.Box, WidgetTemplate):
    '''A widget to display battery status and health.'''

    def __init__(self, battery_name='BAT1'):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.battery_name = battery_name
        self.label = Gtk.Label(label="Power Status")
        Gtk.Box.pack_start(self, self.label, True, True, 0)
        self.data = None
        


    def update(self):
        '''Update method called by ui.py'''
        stats = self.get_battery_stats()
        
        overlays = []

        # Draw lightning bolt icon if charging
        status = stats['status'] if stats['status'] is not None else 'Unknown'
        if status.lower() == 'charging':
            overlays.append({"name": "charging_icon", "path": "overlays/framework-charging-{overlay_id}.png", "color": (0, 255, 0, 255)})

        self.data = {
            "percentage": stats['percentage'],
            "status": stats['status'],
            "health": stats['health'],
            "overlays": overlays
        }

    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''
        
        if self.data:
            percent = self.data['percentage'] if self.data['percentage'] is not None else 'Unknown'
            status = self.data['status'] if self.data['status'] is not None else 'Unknown'
            health = f"{self.data['health']}%" if self.data['health'] is not None else 'Unknown'
            text = f"Battery: {percent}%\nStatus: {status}\nHealth: {health}"
            self.label.set_text(text)
        else:
            self.label.set_text("Power Status\nNo data yet.")


    def get_battery_stats(self):
        '''Returns a dictionary with battery stats: percentage, status, and health.'''

        battery_name = self.battery_name

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
