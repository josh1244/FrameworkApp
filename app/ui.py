'''
Framework Control App
This application provides control features for Framework Laptops.
It displays the laptop model and allows for various controls.
'''

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
from app.model_image import ModelImage
from app.keyboard_backlight import KeyboardBacklightBox

class FrameworkControlApp(Gtk.Window):
    def led_callback_wrapper(self, *args, **kwargs):
        # Call the default handler first
        from app.led_controls import default_on_led_mode_changed, default_on_led_color_clicked
        # Determine which handler to call based on args
        if len(args) > 0 and hasattr(args[0], 'get_label'):
            # Mode button
            default_on_led_mode_changed(*args[:2])
        elif len(args) > 2:
            # Color button
            default_on_led_color_clicked(*args[:3])
        # Now update overlays
        self.on_overlay_widget_changed(*args, **kwargs)
    '''Main application window for Framework Laptop Control.'''

    def __init__(self):
        '''Initialize the Framework Control App window.'''

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

        self.model = get_framework_model()
        self.model.overlays = []
        self.overlay_widgets = []
        self.model_img_widget = None
        self.model_img_parent = None

        # Model (Framework Laptop 13 i5 11th Gen)
        model_label = Gtk.Label(label=self.model.name, xalign=0.5)
        model_label.set_justify(Gtk.Justification.CENTER)
        model_label.set_halign(Gtk.Align.CENTER)
        vbox.pack_start(model_label, False, False, 0)

        # --- Port Images and Laptop Image Section ---
        # Use ExpansionCardUpdater to generate the expansion card UI block
        if self.model.ports > 0:
            exp_updater = ExpansionCards(ports=self.model.ports)
            # Add the model image to the center_space of ExpansionCards
            if self.model.image:
                self.model_img_widget = ModelImage(self.model.image, image_size=320, overlays=self.model.overlays)
                self.model_img_parent = exp_updater.center_space
                self.model_img_parent.pack_start(self.model_img_widget, False, False, 0)
            vbox.pack_start(exp_updater, False, False, 0)
        else:
            # Add laptop image if available (fallback)
            if self.model.image:
                self.model_img_widget = ModelImage(self.model.image, image_size=320)
                self.model_img_parent = vbox
                vbox.pack_start(self.model_img_widget, False, False, 0)

        # Add three individual LED controls horizontally
        leds_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.led_controls = []
        for led_name in ["Left", "Power", "Right"]:
            led_control = LedControlBox(
                led_name,
                on_mode_changed=self.led_callback_wrapper,
                on_color_clicked=self.led_callback_wrapper
            )
            self.led_controls.append(led_control)
            leds_hbox.pack_start(led_control, True, True, 0)
        vbox.pack_start(leds_hbox, False, False, 0)

        # --- Keyboard Backlight Control ---
        self.keyboard_backlight_box = KeyboardBacklightBox()
        vbox.pack_start(self.keyboard_backlight_box, False, False, 0)
        self.overlay_widgets.append(self.keyboard_backlight_box)

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
    def on_overlay_widget_changed(self, *args, **kwargs):
        '''Callback for when an overlay widget changes.
        This updates the model image with the new overlays.'''

        # Gather overlays from all widgets that provide get_overlay()
        overlays = []
        for widget in self.led_controls + self.overlay_widgets:
            if hasattr(widget, "get_overlay"):
                overlay = widget.get_overlay()
                if overlay:
                    overlays.append(overlay)
        self.model.overlays = overlays
        # Remove old model image widget
        if self.model_img_widget and self.model_img_parent:
            self.model_img_parent.remove(self.model_img_widget)
        # Add new model image widget with updated overlays
        self.model_img_widget = ModelImage(self.model.image, image_size=320, overlays=overlays)
        self.model_img_parent.pack_start(self.model_img_widget, False, False, 0)
        self.model_img_parent.show_all()

