#!/usr/bin/env python3
import time
import signal
import sys
import threading
import subprocess

class KeyboardBacklightDaemon:
    def __init__(self):
        self.running = True
        self.mode = 'auto'  # Modes: breathe, auto, manual, responsive
        self.thread = threading.Thread(target=self.run, daemon=True)
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, signum, frame):
        print('Daemon stopping...')
        self.running = False
        self.thread.join()
        sys.exit(0)

    def run(self):
        while self.running:
            # Read mode from IPC file
            try:
                with open("/tmp/kb_backlight_mode", "r", encoding="utf-8") as f:
                    mode = f.read().strip().lower()
                    if mode and mode != self.mode:
                        print(f"Mode changed to: {mode}")
                        self.mode = mode
            except (FileNotFoundError, OSError) as e:
                print(f"Error reading mode file: {e}")

            if self.mode == 'breathe':
                self.breathe_pattern()
            elif self.mode == 'auto':
                self.autobrightness_pattern()
            elif self.mode == 'responsive':
                self.responsive_pattern()
            else:
                time.sleep(0.5)

    def breathe_pattern(self):
        print('Running breathe pattern...')
        for i in range(0, 101):
            self.set_brightness(i)
            # time.sleep(0.03)
        for i in range(100, -1, -1):
            self.set_brightness(i)
            # time.sleep(0.03)

    def autobrightness_pattern(self):
        # Placeholder: Replace with ambient light sensor logic
        print('Running auto brightness pattern...')
        self.set_brightness(50)
        time.sleep(1)

    def responsive_pattern(self):
        # Placeholder: Replace with interactive logic
        print('Running responsive pattern...')
        self.set_brightness(100)
        time.sleep(1)

    def set_brightness(self, value):
        try:
            subprocess.run(["pkexec", "/usr/bin/ectool", "pwmsetkblight", str(value)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to set brightness: {e}")

    def start(self):
        self.thread.start()
        print('Keyboard backlight daemon started.')
        while self.running:
            time.sleep(1)

if __name__ == '__main__':
    daemon = KeyboardBacklightDaemon()
    daemon.start()
