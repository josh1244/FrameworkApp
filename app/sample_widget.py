'''Sample Widget Module
This module defines a sample widget for demonstration purposes.
It inherits from Gtk.Box and implements the WidgetTemplate interface.
'''

import os
import datetime
from gi.repository import Gtk
from PIL import Image, ImageDraw, ImageFont
from app.widget import WidgetTemplate


class SampleWidget(Gtk.Box, WidgetTemplate):
    '''A sample Widget'''

    def __init__(self, model=None, image_size=(500, 710)):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.label = Gtk.Label(label="Sample Widget")
        Gtk.Box.pack_start(self, self.label, True, True, 0)
        self.data = None
        self.model = model
        self.image_size = image_size

        # Update at init
        self.update()
        self.update_visual()

    def update(self):
        # Generate current time string
        now = datetime.datetime.now()
        time_str = now.strftime("%H:%M:%S")

        # Use passed image size
        width, height = self.image_size

        # Generate overlay image with the current time
        overlay_dir = os.path.join(os.path.dirname(__file__), './assets/overlays')
        overlay_path = os.path.abspath(os.path.join(overlay_dir, 'framework11-time.png'))

        # Create a transparent image (size should match overlay requirements)
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Try to use a font from the assets/fonts directory, fallback to default
        font_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'fonts', 'GraphikBold.otf'))
        try:
            font = ImageFont.truetype(font_path, 36)
        except (OSError, IOError):
            font = ImageFont.load_default()

        # Draw the time string in white, centered
        try:
            text_w, text_h = font.getsize(time_str)
        except AttributeError:
            # For newer Pillow versions, use getbbox
            bbox = font.getbbox(time_str)
            text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (img.width - text_w) // 2
        y = int(img.height * .25 - text_h) / 2
        draw.text((x, y), time_str, font=font, fill=(255, 255, 255, 255))

        # Save the overlay image
        os.makedirs(os.path.dirname(overlay_path), exist_ok=True)
        img.save(overlay_path)

        # Set data with overlays key for the UI
        self.data = {
            "time": now.isoformat(),
            "image_size": self.image_size,
            "overlays": [{"name": "time", "path": "overlays/framework11-time.png", "color": None}]
        }

    def update_visual(self):
        # Update the label with the latest data
        if self.data:
            self.label.set_text(f"Sample Widget\nTime: {self.data['time']}")
        else:
            self.label.set_text("Sample Widget\nNo data yet.")
