'''Sample Widget Module
This module defines a sample widget for demonstration purposes.
It inherits from Gtk.Box and implements the WidgetTemplate interface.
'''

import datetime
from gi.repository import Gtk
from app.widget import WidgetTemplate


class SampleWidget(Gtk.Box, WidgetTemplate):
    '''A sample Widget'''

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.label = Gtk.Label(label="Sample Widget")
        Gtk.Box.pack_start(self, self.label, True, True, 0)
        self.data = None

        # Update at init
        self.update()
        self.update_visual()

    def update(self):
        # Simulate generating some data
        self.data = {"time": datetime.datetime.now().isoformat()}

    def update_visual(self):
        # Update the label with the latest data
        if self.data:
            self.label.set_text(f"Sample Widget\nTime: {self.data['time']}")
        else:
            self.label.set_text("Sample Widget\nNo data yet.")
