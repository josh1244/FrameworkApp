"""
power_profiles_controller.py
GTK widget to display and optionally change GNOME/Fedora power profiles using D-Bus.
"""

import threading
import subprocess
try:
    from pydbus import SystemBus # type: ignore
except ImportError:
    SystemBus = None

from gi.repository import Gtk, GLib

class PowerProfilesController(Gtk.Box):
    '''Widget for displaying and changing power profiles.'''

    def __init__(self, update_interval_ms=5000):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        self.label = Gtk.Label(label="Power Profile: ...", xalign=0)
        self.label.set_justify(Gtk.Justification.LEFT)
        self.label.set_halign(Gtk.Align.START)
        self.pack_start(self.label, True, True, 0)
        self.combo = Gtk.ComboBoxText()
        self._combo_handler_id = self.combo.connect("changed", self.on_profile_changed)
        self.pack_start(self.combo, False, False, 0)
        self.bus = None
        self.proxy = None
        self.available_profiles = []
        self.backend = None  # 'ppd' or 'tuned'
        print("[PowerProfilesController] Initializing backend...")
        self._init_backend()
        GLib.timeout_add(update_interval_ms, self._periodic_update)

    def _init_backend(self):
        print("[PowerProfilesController] Checking for power-profiles-daemon...")
        # Try power-profiles-daemon first
        if SystemBus is not None:
            try:
                result = subprocess.run([
                    'systemctl', 'is-active', '--quiet', 'power-profiles-daemon.service'
                ], check=False)
                if result.returncode == 0:
                    print("[PowerProfilesController] Using power-profiles-daemon backend.")
                    self.backend = 'ppd'
                    self.bus = SystemBus()
                    self.proxy = self.bus.get(
                        'net.hadess.PowerProfiles',
                        '/net/hadess/PowerProfiles'
                    )
                    self._update_profiles()
                    return
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"[PowerProfilesController] Could not check power-profiles-daemon status: {e}")
                self.label.set_text(f"Could not check power-profiles-daemon status: {e}")
                return
        # Try tuned
        print("[PowerProfilesController] Checking for tuned...")
        try:
            result = subprocess.run([
                'systemctl', 'is-active', '--quiet', 'tuned.service'
            ], check=False)
            if result.returncode == 0:
                print("[PowerProfilesController] Using tuned backend.")
                self.backend = 'tuned'
                self._update_profiles()
                return
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"[PowerProfilesController] Could not check tuned status: {e}")
            self.label.set_text(f"Could not check tuned status: {e}")
            return
        print("[PowerProfilesController] No supported power profile backend found (power-profiles-daemon or tuned)")
        self.label.set_text("No supported power profile backend found (power-profiles-daemon or tuned)")

    def _update_profiles(self):
        threading.Thread(target=self._update_profiles_thread, daemon=True).start()

    def _update_profiles_thread(self):
        '''Thread to update power profiles without blocking GTK.'''

        # print(f"[PowerProfilesController] Updating profiles (backend: {self.backend})")
        if self.backend == 'ppd':
            # print("[PowerProfilesController] Querying power-profiles-daemon for profiles...")
            if not self.proxy:
                return
            try:
                current = self.proxy.Get('net.hadess.PowerProfiles', 'ActiveProfile')
                available = self.proxy.Get('net.hadess.PowerProfiles', 'Profiles')
                profiles = [profile[0] for profile in available]
                print(f"[PowerProfilesController] Available profiles: {profiles}, current: {current}")
                GLib.idle_add(self._update_profiles_ui, profiles, current, None)
            except AttributeError as e:
                print(f"Failed to get power profile info: {e}")
                GLib.idle_add(self.label.set_text, "PowerProfiles error: Could not read profile info. Is power-profiles-daemon running?")
        elif self.backend == 'tuned':
            # print("[PowerProfilesController] Querying tuned for profiles...")
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
                profiles = []
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
                            name, desc = prof_line.split(' - ', 1)
                            name = name.strip()
                        else:
                            name = prof_line.split()[0]
                        if name in allowed_profiles:
                            profiles.append(name)
                            profile_map[name] = allowed_profiles[name]
                            if line.startswith('* '):
                                current_from_list = name
                current_profile = current_from_list if current_from_list else current
                GLib.idle_add(self._update_profiles_ui, profiles, current_profile, 'tuned', profile_map)
            except (subprocess.CalledProcessError, OSError):
                print("Failed to get tuned profile info.")
                GLib.idle_add(self.label.set_text, "Tuned error: Could not read profile info.")
        else:
            GLib.idle_add(self.label.set_text, "No supported power profile backend found (power-profiles-daemon or tuned)")

    def _update_profiles_ui(self, profiles, current, backend, profile_map=None):
        # Block signal to avoid duplicate 'changed' events
        self.combo.handler_block(self._combo_handler_id)
        self.combo.remove_all()
        self.available_profiles = profiles
        self._profile_display_map = profile_map if profile_map else {name: name for name in profiles}
        for profile in profiles:
            self.combo.append_text(self._profile_display_map[profile])
        if current and current in profiles:
            self.combo.set_active(profiles.index(current))
        self.combo.handler_unblock(self._combo_handler_id)
        if backend == 'tuned':
            self.label.set_text("Power Profile (tuned)")
        else:
            self.label.set_text("Power Profile (ppd)")
        return False

    def _periodic_update(self):
        '''Periodically update the power profiles.'''

        # Run in a thread to avoid blocking GTK
        threading.Thread(target=self._update_profiles, daemon=True).start()
        return True

    def on_profile_changed(self, combo):
        '''Handle profile selection change from the combo box.'''

        print("[PowerProfilesController] Profile selection changed.")
        idx = combo.get_active()
        if idx < 0 or idx >= len(self.available_profiles):
            return
        selected = self.available_profiles[idx]
        # For tuned, only pass the profile name to tuned-adm
        if self.backend == 'tuned' and hasattr(self, '_profile_display_map'):
            print(f"[PowerProfilesController] User selected display: {self.combo.get_active_text()}")
            print(f"[PowerProfilesController] Using tuned profile name: {selected}")
        if self.backend == 'ppd':
            print(f"[PowerProfilesController] Setting power-profiles-daemon profile to: {selected}")
            if not self.proxy:
                return
            try:
                self.proxy.Set('net.hadess.PowerProfiles', 'ActiveProfile', selected)
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"Failed to set power profile: {e}")
                self.label.set_text("Failed to set profile. Do you have permission?")
        elif self.backend == 'tuned':
            print(f"[PowerProfilesController] Setting tuned profile to: {selected}")
            try:
                result = subprocess.run(['tuned-adm', 'profile', selected], capture_output=True, text=True, check=False)
                if result.returncode != 0:
                    err = result.stderr.strip() or result.stdout.strip()
                    if 'does not exist' in err:
                        self.label.set_text(f"Requested profile does not exist: {selected}")
                    else:
                        self.label.set_text(f"Failed to set tuned profile: {err}")
                # Always refresh after attempting to set
                self._update_profiles()
            except (subprocess.CalledProcessError, OSError) as e:
                print(f"Failed to set tuned profile: {e}")
                self.label.set_text("Failed to set tuned profile.")
                self._update_profiles()
