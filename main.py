'''Framework Control App
This application provides control features for Framework Laptops.
It displays the laptop model and allows for various controls.
'''

from app.ui import FrameworkControlApp
from gi.repository import Gtk


if __name__ == "__main__":
    win = FrameworkControlApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
