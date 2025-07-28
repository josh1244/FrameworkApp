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

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.add(box)

    
        self.label = Gtk.Label(label="Power Profile: ...", xalign=0)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_halign(Gtk.Align.START)
        box.pack_start(self.label, False, False, 0)
        self.data = None

        # Setup Power profiles controller
        self.combo = Gtk.ComboBoxText()
        self._combo_handler_id = self.combo.connect("changed", self.on_profile_changed)
        box.pack_start(self.combo, False, False, 0)
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

        # Get the data at init
        self.update()
        self._populate_combo()
        self.update_visual()

    def update(self):
        '''Update method called by ui.py'''

        profiles = []
        current_profile = None

        if self.backend == 'ppd':
            if not self.proxy:
                self.data = {"profiles": [], "current": None}
                return
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
        self.data = {
            "profiles": profiles,
            "current": current_profile,
        }


    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''
        if not self.data or not self.data.get('profiles'):
            self.combo.set_active(-1)
            return
        profiles = self.data['profiles']
        current = self.data['current']
        if current and current in profiles:
            self.combo.set_active(profiles.index(current))
        else:
            self.combo.set_active(-1)


    def _init_backend(self):
        '''Figures out which backend to use for power profiles.'''

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

    def _populate_combo(self):
        """Populate the combo box with available profiles."""
        self.combo.remove_all()
        if not self.data or not self.data.get('profiles'):
            return
        for profile in self.data['profiles']:
            display = self.profile_map.get(profile, profile)
            self.combo.append_text(display)


    def on_profile_changed(self, combo):
        '''Handle profile selection change from the combo box.'''
        if not self.data or not self.data.get('profiles'):
            return
        idx = combo.get_active()
        profiles = self.data['profiles']
        if idx < 0 or idx >= len(profiles):
            return
        selected = profiles[idx]
        self.data['current'] = selected  # Update current profile in data

        if self.backend == 'ppd':
            if not self.proxy:
                return
            try:
                self.proxy.Set('net.hadess.PowerProfiles', 'ActiveProfile', selected)
            except (AttributeError, OSError) as e:
                print(f"[PowerProfilesController] Failed to set power profile: {e}")
                self.label.set_text("Failed to set profile. Do you have permission?")
        elif self.backend == 'tuned':
            try:
                result = subprocess.run(['tuned-adm', 'profile', selected], capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    err = result.stderr.strip() or result.stdout.strip()
                    if 'does not exist' in err:
                        self.label.set_text(f"Requested profile does not exist: {selected}")
                    else:
                        self.label.set_text(f"Failed to set tuned profile: {err}")

                # Always refresh after attempting to set
                self.update_visual()
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[PowerProfilesController] Failed to set tuned profile: {e}")
                self.label.set_text("Failed to set tuned profile.")
                self.update_visual()

