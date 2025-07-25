import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from app.image_utils import load_scaled_image, colorize_image
from app.helpers import get_asset_path

class ModelImage(Gtk.Box):
    '''Widget to display the laptop model image.'''
    def __init__(self, image_name, image_size=320, overlays=None):
        """
        overlays: list of dicts, each dict has keys:
            'name': image name (str)
            'color': optional color filter (tuple or str)
        """
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_halign(Gtk.Align.CENTER)
        self.image_name = image_name
        self.image_size = image_size
        self.overlays = overlays or []
        self._build_ui()

    def _build_ui(self):
        for child in self.get_children():
            self.remove(child)
        overlay = Gtk.Overlay()
        overlay.set_halign(Gtk.Align.CENTER)
        overlay.set_valign(Gtk.Align.CENTER)
        # Add base image
        if self.image_name:
            image_path = get_asset_path(self.image_name)
            base_img_widget = load_scaled_image(image_path, self.image_size)
            if base_img_widget:
                overlay.add(base_img_widget)
            else:
                overlay.add(Gtk.Label(label="[No Image]"))
        else:
            overlay.add(Gtk.Label(label="[No Image]"))
        # Add overlays with optional color filter
        for overlay_info in self.overlays:
            overlay_name = overlay_info.get('name')
            color = overlay_info.get('color')
            overlay_path = get_asset_path(overlay_name)
            if color:
                overlay_img_widget = colorize_image(overlay_path, self.image_size, color)
            else:
                overlay_img_widget = load_scaled_image(overlay_path, self.image_size)
            if overlay_img_widget:
                overlay.add_overlay(overlay_img_widget)
        self.add(overlay)
        self.show()
