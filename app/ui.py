from app.model_image import ModelImage
'''
Framework Control App
This application provides control features for Framework Laptops.
It displays the laptop model and allows for various controls.
'''

import os
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from app.framework_model import get_framework_model
from app.image_utils import load_scaled_image
from app.led_controls import LedControlBox
from app.power_status import PowerStatusBox
from app.power_profiles_controller import PowerProfilesController
from app.expansion_cards import ExpansionCards
from app.helpers import get_asset_path
from app.keyboard_backlight import KeyboardBacklightBox

class FrameworkControlApp(Gtk.Window):
    '''Main application window for Framework Laptop Control.'''

    def __init__(self):
        Gtk.Window.__init__(self, title="Framework Laptop Control")
        self.set_border_width(10)
        self.set_default_size(400, 300)

        # Use a vertical box to hold logo, image, and label
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.add(vbox)

        # Framework logo image
        framework_image_path = get_asset_path("framework.png")
        logo_img = load_scaled_image(framework_image_path, 200)
        if logo_img:
            vbox.pack_start(logo_img, False, False, 0)

        model = get_framework_model()

        # Model (Framework Laptop 13 i5 11th Gen)
        model_label = Gtk.Label(label=model.name, xalign=0.5)
        model_label.set_justify(Gtk.Justification.CENTER)
        model_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(model_label, False, False, 0)

        # --- Port Images and Laptop Image Section ---
        # Use ExpansionCardUpdater to generate the expansion card UI block
        if model.ports > 0:
            exp_updater = ExpansionCards(ports=model.ports)
            # Add the model image to the center_space of ExpansionCards
            if model.image:
                # model.overlays = [
                #     {'name': "overlays/framework11-mic-off.png"},
                #     {'name': "overlays/framework11-camera-off.png"},
                #     {'name': "overlays/framework11-caps-led.png"},
                #     {'name': "overlays/framework11-left-led.png"},
                #     {'name': "overlays/framework11-right-led.png"},
                #     {'name': "overlays/framework11-power-led.png", 'color': (0, 255, 0)}
                # ]

                model_img_widget = ModelImage(model.image, image_size=320, overlays=model.overlays)
                exp_updater.center_space.pack_start(model_img_widget, False, False, 0)
            vbox.pack_start(exp_updater, False, False, 0)
        else:
            # Add laptop image if available (fallback)
            if model.image:
                model_img_widget = ModelImage(model.image, image_size=320)
                vbox.pack_start(model_img_widget, False, False, 0)

        # Add three individual LED controls horizontally
        leds_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        for led_name in ["Left", "Power", "Right"]:
            led_control = LedControlBox(led_name)
            leds_hbox.pack_start(led_control, True, True, 0)
        vbox.pack_start(leds_hbox, False, False, 0)

        # --- Keyboard Backlight Control ---
        keyboard_backlight_box = KeyboardBacklightBox()
        vbox.pack_start(keyboard_backlight_box, False, False, 0)


        # --- Battery Stats ---
        power_status_box = PowerStatusBox()
        vbox.pack_start(power_status_box, True, True, 0)

        # --- Power Profiles ---
        power_profiles_controller = PowerProfilesController()
        vbox.pack_start(power_profiles_controller, True, True, 0)

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

    