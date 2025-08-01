"""
power_profiles_controller.py
GTK widget to display and optionally change GNOME/Fedora power profiles using D-Bus.
"""

import subprocess
try:
    from pydbus import SystemBus # type: ignore
except ImportError:
    SystemBus = None

from gi.repository import Gtk, GLib
from app.widget import WidgetTemplate


class PowerProfilesWidget(Gtk.Box, WidgetTemplate):
    '''Widget for displaying and changing power profiles.'''

    def __init__(self):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)

        vertical_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        self.add(vertical_box) 


        power_profiles_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        vertical_box.add(power_profiles_box)

        sleep_mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        vertical_box.add(sleep_mode_box)

        self.init_power_profiles(power_profiles_box)
        self.init_sleep_modes(sleep_mode_box)

        # Get the data at init
        self.update()
        self._populate_power_profile_buttons()

    def update(self):
        '''Update method called by ui.py'''

        profiles, current_profile = self.update_power_profiles()
        self.current_sleep_mode = self.get_current_sleep_mode()
        self.data = {
            "power_profiles": profiles,
            "current_power_profile": current_profile,
            'current_sleep_mode': self.current_sleep_mode,
            'available_sleep_modes': self.sleep_modes
        }
    
    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''

        self.update_power_profile_visuals()
        self.update_sleep_mode_visuals()
    

    def _init_backend(self):
        '''Figures out which backend to use for power profiles.'''

        self.init_power_profiles_backend()



    def init_power_profiles(self, box):
        self.label = Gtk.Label(label="Power Profile: ...", xalign=0)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_halign(Gtk.Align.START)
        box.pack_start(self.label, False, False, 0)
        self.data = None

        # Setup Power profiles controller
        self.button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(self.button_box, False, False, 0)
        self.profile_buttons = {}
        self.proxy = None
        self.backend = None  # 'ppd' or 'tuned'
        self.profile_map = {}  # name -> display string
        print("[PowerProfilesController] Initializing backend...")
        self._init_backend()

        # Set label based on backend
        if self.backend == 'tuned':
            self.label.set_text("Power Profile (tuned)")
        elif self.backend == 'ppd':
            self.label.set_text("Power Profile (ppd)")
        else:
            self.label.set_text("No supported power profile backend found (power-profiles-daemon or tuned)")

    def _populate_power_profile_buttons(self):
        """Populate the button box with profile buttons."""
        for child in self.button_box.get_children():
            self.button_box.remove(child)
        self.profile_buttons = {}
        self.profile_button_handlers = {}
        # Define icons for each profile
        icon_map = {
            "powersave": "power-profile-power-saver-symbolic",
            "balanced-battery": "power-profile-balanced-symbolic",
            "throughput-performance": "power-profile-performance-symbolic"
        }
        for profile in ["powersave", "balanced-battery", "throughput-performance"]:
            display = self.profile_map.get(profile, profile)
            btn = Gtk.ToggleButton()
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
            # Icon
            icon_name = icon_map.get(profile, None)
            if icon_name:
                img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
                hbox.pack_start(img, False, False, 0)
            # Text
            lbl = Gtk.Label(label=display)
            hbox.pack_start(lbl, False, False, 0)
            btn.add(hbox)
            handler_id = btn.connect("toggled", self.on_power_profile_button_toggled, profile)
            self.profile_button_handlers[profile] = handler_id
            self.button_box.pack_start(btn, False, False, 0)
            self.profile_buttons[profile] = btn
        self.button_box.show_all()
        self.update_visual()  # Ensure selection is shown after populating buttons

    def init_sleep_modes(self, box):
        self.sleep_modes = self.get_available_sleep_modes()
        self.current_mode = None
        self.data = {}

        # GUI elements
        self.sleep_label = Gtk.Label(label="Current sleep mode: Unknown")
        box.pack_start(self.sleep_label, False, False, 0)

        self.sleep_button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        box.pack_start(self.sleep_button_box, False, False, 0)
        self.sleep_mode_buttons = {}
        self.sleep_mode_handlers = {}
        for mode in self.sleep_modes:
            btn = Gtk.ToggleButton(label=mode)
            handler_id = btn.connect("toggled", self.on_sleep_mode_toggled, mode)
            self.sleep_mode_handlers[mode] = handler_id
            self.sleep_button_box.pack_start(btn, False, False, 0)
            self.sleep_mode_buttons[mode] = btn
        self.sleep_button_box.show_all()
        # self.update_sleep_mode_visuals()
    
    def update_power_profiles(self):
        profiles = []
        current_profile = None

        if self.backend == 'ppd':
            if not self.proxy:
                return [], None
            try:
                current = self.proxy.Get('net.hadess.PowerProfiles', 'ActiveProfile')
                available = self.proxy.Get('net.hadess.PowerProfiles', 'Profiles')
                profiles = [profile[0] for profile in available]
                print(f"[PowerProfilesController] Available profiles: {profiles}, current: {current}")
                self.profile_map = {name: name for name in profiles}
                current_profile = current
            except (AttributeError, OSError) as e:
                print(f"[PowerProfilesController] Failed to get power profile info: {e}")
                GLib.idle_add(self.label.set_text, "PowerProfiles error: Could not read profile info. Is power-profiles-daemon running?")
        elif self.backend == 'tuned':
            try:
                # Get current profile
                result = subprocess.run(['tuned-adm', 'active'], capture_output=True, text=True, check=False)
                current = None
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if 'Current active profile:' in line:
                            current = line.split(':', 1)[1].strip()
                            if current == "balanced":
                                current = "balanced-battery"
                # Get available profiles
                result = subprocess.run(['tuned-adm', 'list'], capture_output=True, text=True, check=False)
                profile_map = {}  # name -> display string
                current_from_list = None
                allowed_profiles = {
                    "powersave": "Powersave",
                    "balanced-battery": "Balanced",
                    "throughput-performance": "Performance"
                }
                for line in result.stdout.splitlines():
                    if line.startswith('- ') or line.startswith('* '):
                        prof_line = line[2:].strip()
                        # Split on first space or dash for name/desc
                        if ' - ' in prof_line:
                            name, _ = prof_line.split(' - ', 1)
                            name = name.strip()
                        else:
                            name = prof_line.split()[0]
                        if name in allowed_profiles:
                            profiles.append(name)
                            profile_map[name] = allowed_profiles[name]
                            if line.startswith('* '):
                                current_from_list = name
                current_profile = current_from_list if current_from_list else current
                self.profile_map = profile_map
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[PowerProfilesController] Failed to get tuned profile info: {e}")
                GLib.idle_add(self.label.set_text, "Tuned error: Could not read profile info.")
        else:
            GLib.idle_add(self.label.set_text, "No supported power profile backend found (power-profiles-daemon or tuned)")
        
        return profiles, current_profile


    def get_current_sleep_mode(self):
        '''Get the current sleep mode from the system'''

        try:
            with open('/sys/power/mem_sleep', 'r', encoding='utf-8') as f:
                modes = f.read().strip()
            # The current mode is wrapped in brackets, e.g. "s2idle [deep]"
            for mode in self.sleep_modes:
                if f'[{mode}]' in modes:
                    return mode
            return None
        except OSError:
            return None


    def update_power_profile_visuals(self):
        if not self.data or not self.data.get('power_profiles'):
            for btn in self.profile_buttons.values():
                btn.set_sensitive(False)
                btn.set_active(False)
            return
        profiles = self.data['power_profiles']
        current = self.data['current_power_profile']
        for name, btn in self.profile_buttons.items():
            btn.set_sensitive(name in profiles)
            handler_id = self.profile_button_handlers.get(name)
            if handler_id is not None:
                btn.handler_block(handler_id)
            btn.set_active(name == current)
            if handler_id is not None:
                btn.handler_unblock(handler_id)

    def update_sleep_mode_visuals(self):
        if self.current_sleep_mode:
            self.sleep_label.set_text(f"Current sleep mode: {self.current_sleep_mode}")
            # Set button states
            for mode, btn in self.sleep_mode_buttons.items():
                handler_id = self.sleep_mode_handlers.get(mode)
                if handler_id is not None:
                    btn.handler_block(handler_id)
                btn.set_active(mode == self.current_sleep_mode)
                if handler_id is not None:
                    btn.handler_unblock(handler_id)
        else:
            self.sleep_label.set_text("Current sleep mode: Unknown")
            for btn in self.sleep_mode_buttons.values():
                btn.set_active(False)


    def init_power_profiles_backend(self):
        print("[PowerProfilesController] Checking for power-profiles-daemon...")
        # Try power-profiles-daemon first
        if SystemBus is not None:
            try:
                result = subprocess.run([
                    'systemctl', 'is-active', '--quiet', 'power-profiles-daemon.service'
                ], check=False)
                if result.returncode == 0:
                    self.backend = 'ppd'
                    self.proxy = SystemBus().get(
                        'net.hadess.PowerProfiles',
                        '/net/hadess/PowerProfiles'
                    )
                    return
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[PowerProfilesController] Could not check power-profiles-daemon status: {e}")
                self.label.set_text(f"Could not check power-profiles-daemon status: {e}")
                return
        # Try tuned
        try:
            result = subprocess.run([
                'systemctl', 'is-active', '--quiet', 'tuned.service'
            ], check=False)
            if result.returncode == 0:
                self.backend = 'tuned'
                return
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"[PowerProfilesController] Could not check tuned status: {e}")
            self.label.set_text(f"Could not check tuned status: {e}")
            return
        print("[PowerProfilesController] No supported power profile backend found (power-profiles-daemon or tuned)")
        self.label.set_text("No supported power profile backend found (power-profiles-daemon or tuned)")

    def on_power_profile_button_toggled(self, button, profile):
        '''Handle profile button toggled.'''
        if not self.data or not self.data.get('power_profiles'):
            return
        if profile not in self.data['power_profiles']:
            return
        if not button.get_active():
            # Prevent unselecting the active button (only one can be active)
            handler_id = self.profile_button_handlers.get(profile)
            if handler_id is not None:
                button.handler_block(handler_id)
            button.set_active(True)
            if handler_id is not None:
                button.handler_unblock(handler_id)
            return
        self.data['current_power_profile'] = profile  # Update current profile in data
        # Unset all other buttons
        for name, btn in self.profile_buttons.items():
            if name != profile:
                handler_id = self.profile_button_handlers.get(name)
                if handler_id is not None:
                    btn.handler_block(handler_id)
                btn.set_active(False)
                if handler_id is not None:
                    btn.handler_unblock(handler_id)

        if self.backend == 'ppd':
            if not self.proxy:
                return
            try:
                self.proxy.Set('net.hadess.PowerProfiles', 'ActiveProfile', profile)
            except (AttributeError, OSError) as e:
                print(f"[PowerProfilesController] Failed to set power profile: {e}")
                self.label.set_text("Failed to set profile. Do you have permission?")
        elif self.backend == 'tuned':
            try:
                result = subprocess.run(['tuned-adm', 'profile', profile], capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    err = result.stderr.strip() or result.stdout.strip()
                    if 'does not exist' in err:
                        self.label.set_text(f"Requested profile does not exist: {profile}")
                    else:
                        self.label.set_text(f"Failed to set tuned profile: {err}")
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[PowerProfilesController] Failed to set tuned profile: {e}")
                self.label.set_text("Failed to set tuned profile.")


    def on_sleep_mode_toggled(self, button, mode):
        '''Set sleep mode when button is pressed'''
        if not button.get_active():
            # Prevent unselecting the active button (only one can be active)
            handler_id = self.sleep_mode_handlers.get(mode)
            if handler_id is not None:
                button.handler_block(handler_id)
            button.set_active(True)
            if handler_id is not None:
                button.handler_unblock(handler_id)
            return
        # Unset all other buttons
        for m, btn in self.sleep_mode_buttons.items():
            if m != mode:
                handler_id = self.sleep_mode_handlers.get(m)
                if handler_id is not None:
                    btn.handler_block(handler_id)
                btn.set_active(False)
                if handler_id is not None:
                    btn.handler_unblock(handler_id)
        # Set the sleep mode
        if self.set_sleep_mode(mode):
            self.current_sleep_mode = mode
            self.sleep_label.set_text(f"Current sleep mode: {mode}")
        else:
            self.sleep_label.set_text("Failed to change sleep mode. Try running as root.")


    def get_available_sleep_modes(self):
        '''Get available sleep modes from the system'''

        # Example: return a list of supported sleep modes
        # This could be customized for your system
        return ['s2idle', 'deep']


    def set_sleep_mode(self, mode):
        '''Set the sleep mode on the system'''

        if mode not in self.sleep_modes:
            raise ValueError(f"Invalid sleep mode: {mode}")
        try:
            # Use pkexec to echo the mode into the file with root privileges
            cmd = [
                'pkexec', 'sh', '-c', f'echo {mode} > /sys/power/mem_sleep'
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.returncode == 0
        except Exception:
            return False
