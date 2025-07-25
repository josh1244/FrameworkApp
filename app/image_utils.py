'''This module provides utility functions for loading and scaling images in a GTK application.'''


import os
import sys
from gi.repository import Gtk, GdkPixbuf, GLib


def load_scaled_image(path, target_width):
    """Load and scale an image to the given width, keeping aspect ratio. 
    Returns Gtk.Image or None."""

    if not os.path.isfile(path):
        print(f"Warning: Image not found at {path}", file=sys.stderr)
        return None
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        if pixbuf.get_width() > target_width:
            scale = target_width / pixbuf.get_width()
            target_height = int(pixbuf.get_height() * scale)
            pixbuf = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)
        img = Gtk.Image.new_from_pixbuf(pixbuf)
    except GLib.Error as e:
        print(f"Warning: Could not scale image: {e}", file=sys.stderr)
        img = Gtk.Image.new_from_file(path)
    return img


def colorize_image(path, target_width, color):
    """
    Load and scale an image, then apply a color filter (RGBA tuple or hex string).
    Returns Gtk.Image or None.
    """

    if not os.path.isfile(path):
        print(f"Warning: Image not found at {path}", file=sys.stderr)
        return None
    try:
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(path)
        if pixbuf.get_width() > target_width:
            scale = target_width / pixbuf.get_width()
            target_height = int(pixbuf.get_height() * scale)
            pixbuf = pixbuf.scale_simple(target_width, target_height, GdkPixbuf.InterpType.BILINEAR)
        # Parse color
        if isinstance(color, str):
            if color.startswith('#'):
                color = color.lstrip('#')
                lv = len(color)
                color = tuple(int(color[i:i+2], 16) for i in range(0, lv, 2))
        # Default to opaque if alpha not provided
        if len(color) == 3:
            color = (*color, 255)
        r, g, b, a = (int(c) for c in color)
        # Blend color filter with original image, preserving transparency
        width, height = pixbuf.get_width(), pixbuf.get_height()
        has_alpha = pixbuf.get_has_alpha()
        n_channels = pixbuf.get_n_channels()
        rowstride = pixbuf.get_rowstride()
        pixels = pixbuf.get_pixels()
        import array
        # Copy pixels to a mutable array
        arr = array.array('B', pixels)
        for y in range(height):
            for x in range(width):
                i = y * rowstride + x * n_channels
                orig_r = arr[i]
                orig_g = arr[i+1]
                orig_b = arr[i+2]
                orig_a = arr[i+3] if has_alpha and n_channels == 4 else 255
                # Blend: multiply color and preserve alpha
                arr[i]   = int(orig_r * r / 255)
                arr[i+1] = int(orig_g * g / 255)
                arr[i+2] = int(orig_b * b / 255)
                if has_alpha and n_channels == 4:
                    arr[i+3] = int(orig_a * a / 255)
        # Create new pixbuf from blended data
        blended = GdkPixbuf.Pixbuf.new_from_data(
            arr.tobytes(),
            GdkPixbuf.Colorspace.RGB,
            has_alpha,
            8,
            width,
            height,
            rowstride
        )
        img = Gtk.Image.new_from_pixbuf(blended)
    except GLib.Error as e:
        print(f"Warning: Could not colorize image: {e}", file=sys.stderr)
        img = Gtk.Image.new_from_file(path)
    return img
