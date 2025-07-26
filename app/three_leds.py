'''Add three individual LED controls vertically'''

from gi.repository import Gtk
from app.led_controls import LedControlBox


class ThreeLEDs(Gtk.Box):
    '''Widget to contain the three LEDS'''

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        leds_hbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.led_controls = []
        for led_name in ["Left", "Power", "Right"]:
            led_control = LedControlBox(
                led_name,
                # on_mode_changed=self.led_callback_wrapper,
                # on_color_clicked=self.led_callback_wrapper
            )
            self.led_controls.append(led_control)
            leds_hbox.pack_start(led_control, True, True, 0)
        self.pack_start(leds_hbox, False, False, 0)