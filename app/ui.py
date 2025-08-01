
# Framework Control App
# This application provides control features for Framework Laptops.
# It displays the laptop model and allows for various controls.


# Standard library
import concurrent.futures

# Third-party
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

# Local application imports
from app.framework_model import get_framework_model
from app.helpers import get_asset_path
from app.image_utils import load_scaled_image
from app.model_image import ModelImage
from app.power_profiles_widget import PowerProfilesWidget
from app.expansion_cards_widget import ExpansionCardsWidget
from app.keyboard_backlight_widget import KeyboardBacklightWidget
from app.sample_widget import SampleWidget
from app.sleep_mode_widget import SleepModeWidget
from app.led_widget import LedWidget
from app.power_status_widget import PowerStatusWidget
from app.system_stats_widget import SystemStatsWidget

UPDATE_INTERVAL_MS=5000
LAPTOP_WIDTH=500


class FrameworkControlApp(Gtk.Window):
    '''The class that defines the application and calls all the widgets'''
    
    def __init__(self):
        '''Initialize the Framework Control App window.'''

        # Set up the window

        Gtk.Window.__init__(self, title="Framework Laptop Control")
        self.set_border_width(10)
        self.set_default_size(400, 300)


        # Set font to Graphik using CSS (try 'Graphik' and set weight), and style sidebar
        css = b"""
        * {
            font-family: 'Graphik', sans-serif;
            font-weight: 500;
        }
        .sidebar-tabs {
            background: #e0e0e0;
            border-radius: 8px;
            padding: 10px 0;
        }
        .sidebar-tab-btn {
            background: transparent;
            border: none;
            box-shadow: none;
            transition: background 0.2s;
        }
        .sidebar-tab-btn:hover {
            background: #cccccc;
        }
        .sidebar-tab-btn:checked, .sidebar-tab-btn:active {
            background: #b0b0b0;
            border-radius: 6px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }
        """
        style_provider = Gtk.CssProvider()
        style_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            self.get_screen(),
            style_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # Figure out the laptop stuff
        self.model = get_framework_model()
        self.model.overlays = []
        self.overlay_widgets = []
        self.model_img_widget = None
        self.model_img_parent = None
        self.current_widget = None
        self._last_overlays = None  # Cache for overlays



        # Create a horizontal box to split sidebar (tabs) and main content (image)
        tab_and_content_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.add(tab_and_content_container)

        # Sidebar: vertical box for tab buttons with icons only, grey background
        tab_sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        tab_sidebar.set_halign(Gtk.Align.FILL)
        tab_sidebar.set_valign(Gtk.Align.FILL)
        tab_sidebar.set_size_request(0, -1) # TODO: Check this
        tab_sidebar.get_style_context().add_class("sidebar-tabs")


        # Define the tabs here (name, icon, widget)
        # All widgets should inherit from WidgetTemplate
        tab_items = [
            ("Stats", "system-run-symbolic", SystemStatsWidget(model=self.model)),
            ("Power", "battery-full-symbolic", PowerProfilesWidget()),
            ("Battery", "battery-good-symbolic", PowerStatusWidget()),
            ("Expansion", "media-flash-symbolic", ExpansionCardsWidget()),
            ("LEDs", "dialog-information-symbolic", LedWidget()),
            ("Keyboard", "keyboard-brightness-symbolic", KeyboardBacklightWidget()),
            ("Sample", "applications-system-symbolic", SampleWidget(self.model.name, (LAPTOP_WIDTH, 710))), # TODO this is hard coded? TODO Model is not used right now...
        ]
        self.tab_buttons = []
        # Store widgets by name for easy access
        self.widgets = {name: widget for name, _icon, widget in tab_items}
        # Store widget data here for access by ui.py and others
        self.widgets_data = {name: None for name, _icon, _widget in tab_items}



        tab_and_content_container.pack_start(tab_sidebar, False, False, 0)

        # Split main content and laptop side by side
        main_and_image_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)

        # Main content:
        main_content_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)

        # Framework logo image
        framework_image_path = get_asset_path("framework.png")
        logo_img = load_scaled_image(framework_image_path, 200)
        if logo_img:
            main_content_container.pack_start(logo_img, False, False, 0)

        # Model Name (ex. Framework Laptop 13 i5 11th Gen)
        model_label = Gtk.Label(label=self.model.name, xalign=0.5)
        model_label.set_justify(Gtk.Justification.CENTER)
        model_label.set_halign(Gtk.Align.CENTER)
        main_content_container.pack_start(model_label, False, False, 0)

        # Stack for widgets
        self.widget_stack = Gtk.Stack()
        for name, icon_name, widget in tab_items:
            self.widget_stack.add_titled(widget, name, name)
        main_content_container.pack_start(self.widget_stack, True, True, 0)

        # Add the tabs to sidebar
        self.tab_buttons = []
        self.tab_handlers = []

        for idx, (name, icon_name, widget) in enumerate(tab_items):
            tab_button = Gtk.ToggleButton()
            tab_button.set_relief(Gtk.ReliefStyle.NONE)
            tab_button.get_style_context().add_class("sidebar-tab-btn")
            image = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
            tab_button.add(image)
            tab_button.set_active(idx == 0)  # First tab active by default
            handler_id = tab_button.connect("toggled", self.on_tab_clicked, idx, name)
            self.tab_buttons.append(tab_button)
            self.tab_handlers.append(handler_id)
            tab_sidebar.pack_start(tab_button, False, False, 0)

        self.widget_stack.set_visible_child_name(tab_items[0][0])  # Show first tab by default

        # Laptop Image
        laptop_image_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        laptop_image_box.set_halign(Gtk.Align.CENTER)
        laptop_image_box.set_valign(Gtk.Align.CENTER)

        if self.model.image:
            self.model_img_widget = ModelImage(self.model.image, image_size=LAPTOP_WIDTH, overlay_id=self.model.overlay_id)
            self.model_img_parent = laptop_image_box
            laptop_image_box.pack_start(self.model_img_widget, False, False, 0)
        else:
            laptop_image_box.pack_start(Gtk.Label(label="[No Image]"), False, False, 0)
 
        # Pack both main_content_container and laptop_image_box into main_and_image_container
        main_and_image_container.pack_start(main_content_container, True, True, 0)
        main_and_image_container.pack_start(laptop_image_box, False, False, 0)

        # Now pack main_and_image_container into tab_and_content_container
        tab_and_content_container.pack_start(main_and_image_container, True, True, 0)

        # Thread pool for async updates
        self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=2)

        # Update at init
        GLib.idle_add(self.update_loop)

        # Start update loop
        GLib.timeout_add(UPDATE_INTERVAL_MS, self._periodic_update)


    def _periodic_update(self):
        # Run update_loop in a background thread
        self._executor.submit(self._background_update_loop)
        return True

    def _background_update_loop(self):
        # Run the heavy update logic in a thread, then schedule UI update on main thread
        visible_name = self.widget_stack.get_visible_child_name()
        widgets_data = {}
        update_errors = {}
        for name, widget in self.widgets.items():
            try:
                # Update the widget data
                widget.update()
                widgets_data[name] = getattr(widget, 'data', None)
            except NotImplementedError as e:
                update_errors[name] = f"NotImplementedError: {e}"
                widgets_data[name] = None
            except (AttributeError, RuntimeError) as e:
                update_errors[name] = f"Error: {e}"
                widgets_data[name] = None

        # Schedule UI update on main thread
        GLib.idle_add(self._finish_update_loop, widgets_data, visible_name)

    def _finish_update_loop(self, widgets_data, visible_name):
        # Update widgets_data and call update_visual for visible widget
        self.widgets_data = widgets_data
        if visible_name in self.widgets:
            try:
                self.widgets[visible_name].update_visual()
            except Exception as e:
                print(f"Error updating visual for widget {visible_name}: {e}")

        # Update laptop image overlays only if overlays have changed
        overlays = self.get_all_widget_overlays()
        if overlays != self._last_overlays:
            self._last_overlays = list(overlays) if overlays is not None else None
            if self.model.image and self.model_img_parent:
                # Remove the old image widget if it exists
                if self.model_img_widget:
                    self.model_img_parent.remove(self.model_img_widget)
                # Create new ModelImage with overlays
                self.model_img_widget = ModelImage(self.model.image, image_size=LAPTOP_WIDTH, overlays=overlays, overlay_id=self.model.overlay_id)
                self.model_img_parent.pack_start(self.model_img_widget, False, False, 0)
                self.model_img_parent.show_all()
        return False  # Only run once per call

    # Update loop function
    def update_loop(self):
        '''A single update loop that gets all the info'''
        # For backward compatibility, run the background update loop
        self._executor.submit(self._background_update_loop)

    # Sidebar tab button function
    def on_tab_clicked(self, _btn, idx, name):
        ''' When click on a sidebar tab, change the current_widget'''

        # Prevent recursion by blocking handlers
        for i, b in enumerate(self.tab_buttons):
            handler_id = self.tab_handlers[i]
            b.handler_block(handler_id)
            b.set_active(i == idx)
            b.handler_unblock(handler_id)
        self.widget_stack.set_visible_child_name(name)

        # Update the current widget
        if name and name in self.widgets:
            try:
                self.widgets[name].update_visual()
            except Exception as e:
                print(f"Error updating visual for widget {name}: {e}")


    def get_all_widget_overlays(self):
        """
        Parse all widgets' data and collect overlay information.
        Expects each widget's data (if present) to have an 'overlays' key (list or None).
        Returns a list of overlays from all widgets.
        """
        overlays = []
        for _name, data in self.widgets_data.items():
            if data and isinstance(data, dict) and 'overlays' in data and data['overlays']:
                overlays.extend(data['overlays'])

        return overlays