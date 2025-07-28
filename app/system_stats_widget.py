'''System Stats Widget Module
This module defines a widget for displaying CPU, memory, storage, and graphics stats.
It inherits from Gtk.Box and implements the WidgetTemplate interface.
'''

import os
import re
import psutil
import platform
from gi.repository import Gtk
from PIL import Image, ImageDraw, ImageFont
from app.widget import WidgetTemplate

class SystemStatsWidget(Gtk.Box, WidgetTemplate):
    '''A widget to display CPU, memory, storage, and graphics stats.'''

    def __init__(self, model=None, image_size=(500, 710)):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=10)
        WidgetTemplate.__init__(self)
        self.label = Gtk.Label(label="System Stats")
        Gtk.Box.pack_start(self, self.label, True, True, 0)
        self.data = None
        self.model = model
        self.image_size = image_size


        stats = self.get_system_stats()
        overlay_path = self.get_os_overlay_path()
        self.data = {
            "stats": stats,
            "image_size": self.image_size,
            "overlays": [
                {"name": "os", "path": overlay_path, "color": None}
            ]
        }

        if self.data:
            stats = self.data['stats']
            cpu = getattr(self.model, 'cpu', 'Unknown') if self.model else 'Unknown'
            text = (f"CPU: {cpu}\n"
                    f"Graphics: {stats['graphics']}\n"
                    f"Memory: {stats['memory']}\n"
                    f"Storage: {stats['storage']}\n")
            self.label.set_text(text)
        else:
            self.label.set_text("System Stats\nNo data yet.")

        
    def update(self):
        '''Update method called by ui.py'''

    def get_os_overlay_path(self):
        '''Return the path to a distro/OS-specific overlay image, generating a 500x710 PNG with the logo at 50%x25%.'''
        system = platform.system().lower()
        overlay_dir = os.path.join(os.path.dirname(__file__), './assets/overlays')
        if system == 'linux':
            distro = self.get_linux_distro()
            distro_map = {
                'fedora': 'os-fedora.png',
                'arch': 'os-arch.png',
                'ubuntu': 'os-ubuntu.png',
                'debian': 'os-debian.png',
                'manjaro': 'os-manjaro.png',
                'pop': 'os-pop.png',
                'opensuse': 'os-opensuse.png',
                'elementary': 'os-elementary.png',
                'mint': 'os-mint.png',
            }
            filename = None
            for key, fname in distro_map.items():
                if key in distro:
                    filename = fname
                    break
            if not filename:
                filename = 'os-linux.png'
        elif system == 'windows':
            filename = 'os-windows.png'
        elif system == 'darwin':
            filename = 'os-macos.png'
        else:
            filename = 'os-unknown.png'
        logo_path = os.path.abspath(os.path.join(overlay_dir, filename))
        out_path = os.path.abspath(os.path.join(overlay_dir, f'os-overlay-{filename}'))
        # Generate overlay if not present
        if not os.path.exists(out_path):
            self.generate_logo_overlay(logo_path, out_path, (500, 710))
        return f"overlays/{os.path.basename(out_path)}"

    def generate_logo_overlay(self, logo_path, out_path, size):
        '''Create a transparent PNG of given size with the logo centered at 50%x25%.'''
        width, height = size
        try:
            base = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            if os.path.exists(logo_path):
                logo = Image.open(logo_path).convert('RGBA')
                # Resize logo to fit nicely (e.g., 128x128 or 20% of width)
                max_logo_w = int(width * 0.2)
                max_logo_h = int(height * 0.2)
                logo.thumbnail((max_logo_w, max_logo_h), Image.LANCZOS)
                logo_w, logo_h = logo.size
                x = int(width * 0.5 - logo_w / 2)
                y = int(height * 0.25 - logo_h / 2)
                base.paste(logo, (x, y), logo)
            base.save(out_path)
        except Exception as e:
            print(f"Failed to generate overlay: {e}")

    def get_linux_distro(self):
        '''Detect Linux distribution name (lowercase, no spaces).'''
        try:
            # Try /etc/os-release (most modern distros)
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('ID='):
                        return line.strip().split('=', 1)[1].replace('"', '').lower()
                    if line.startswith('NAME='):
                        return line.strip().split('=', 1)[1].replace('"', '').lower()
        except Exception:
            pass
        return 'linux'

    def update_visual(self):
        '''Update the visual representation of the widget called by ui.py'''
        
    def get_system_stats(self):
        '''Gather memory, storage, and graphics stats.'''
        # Memory amount (total)
        mem = psutil.virtual_memory()
        mem_total_mb = mem.total / (1000**2)
        memory_gb = mem_total_mb / 1000
        memory = f"{memory_gb:.1f}GB"
        disk = psutil.disk_usage('/')
        total_gb = disk.total / (1000**3)
        if total_gb >= 1000:
            storage = f"{total_gb / 1000:.1f}TB"
        else:
            storage = f"{total_gb:.1f}GB"
        # Try to get graphics info from lspci (Linux)
        graphics = 'Unknown'
        try:
            with os.popen(r"lspci | grep -i 'vga\|3d\|display'") as f:
                out = f.read().strip()
                if out:
                    # Extract only the text inside brackets []
                    match = re.search(r'\[(.*?)\]', out)
                    if match:
                        graphics = match.group(1).strip()
                    else:
                        graphics = 'Unknown'
        except Exception:
            pass
        return {
            'memory': memory,
            'storage': storage,
            'graphics': graphics
        }



