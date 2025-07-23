from ui import FrameworkControlApp
from gi.repository import Gtk

if __name__ == "__main__":
    win = FrameworkControlApp()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()
