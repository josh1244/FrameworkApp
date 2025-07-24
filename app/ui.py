'''
Framework Control App
This application provides control features for Framework Laptops.
It displays the laptop model and allows for various controls.
'''

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from app.framework_model import get_framework_model
from app.image_utils import load_scaled_image


class FrameworkControlApp(Gtk.Window):
    '''Main application window for Framework Laptop Control.'''
  
    def __init__(self):
        Gtk.Window.__init__(self, title="Framework Laptop Control")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Use a vertical box to hold logo, image, and label
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Add Framework logo at the top
        framework_image_path = self.get_asset_path("framework.png")

        logo_img = load_scaled_image(framework_image_path, 200)
        if logo_img:
            vbox.pack_start(logo_img, False, False, 0)

        model = get_framework_model()

        # Add model name label between images
        model_label = Gtk.Label(label=model.name, xalign=0.5)
        model_label.set_justify(Gtk.Justification.CENTER)
        model_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(model_label, False, False, 0)

        # Add laptop image if available
        if model.image:
            image_path = self.get_asset_path(model.image)
            laptop_img = load_scaled_image(image_path, 320)
            if laptop_img:
                vbox.pack_start(laptop_img, False, False, 0)

        items = [
            "LED controls",
            "Fan",
            "Battery",
            "Power profile",
            "Plugged In",
            "On Battery",
            "Sleep Type"
        ]

        label_text = "\n".join(items)
        label = Gtk.Label(label=label_text, xalign=0)
        label.set_justify(Gtk.Justification.LEFT)
        label.set_halign(Gtk.Align.START)
        vbox.pack_start(label, True, True, 0)

        # Set font to Graphik using CSS (try 'Graphik' and set weight)
        css = b"""
        * {
            font-family: 'Graphik', sans-serif;
            font-weight: 500;
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def get_asset_path(self, filename):
        '''Returns the path to the specified asset image.'''
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", filename)
