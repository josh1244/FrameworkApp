import os
import sys
from gi.repository import Gtk

def load_scaled_image(path, target_width):
    """Load and scale an image to the given width, keeping aspect ratio. Returns Gtk.Image or None."""
    if not os.path.isfile(path):
        print(f"Warning: Image not found at {path}", file=sys.stderr)
        return None
    try:
        from gi.repository import GdkPixbuf
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        if pixbuf.get_width() > target_width:
            scale = target_width / pixbuf.get_width()
            target_height = int(pixbuf.get_height() * scale)
            pixbuf = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
    except Exception as e:
        print(f"Warning: Could not scale image: {e}", file=sys.stderr)
        img = Gtk.Image.new_from_file(path)
    return img
