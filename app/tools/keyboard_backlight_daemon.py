#!/usr/bin/env python3

'''Daemon to control keyboard backlight patterns based on user input and system events.
This daemon listens for mode changes and applies the corresponding keyboard backlight pattern.
It supports multiple modes including breathe, auto, manual, and responsive.
'''

import time
import signal
import sys
import threading
import subprocess
from evdev import InputDevice, categorize, ecodes, list_devices

class KeyboardBacklightDaemon:
    '''Daemon to manage keyboard backlight patterns.
    Handles different modes like breathe, auto, manual, and responsive.
    Monitors keyboard input and adjusts backlight accordingly.
    '''

    def __init__(self):
        self.running = True
        self.mode = 'auto'  # Modes: breathe, auto, manual, responsive
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.pattern_thread = None
        self.stop_pattern = False
        signal.signal(signal.SIGTERM, self.handle_exit)
        signal.signal(signal.SIGINT, self.handle_exit)

    def handle_exit(self, _signum, _frame):
        '''Handle exit signals to stop the daemon gracefully.'''

        print('Daemon stopping...')
        self.running = False
        self.thread.join()
        sys.exit(0)

    def run(self):
        '''Main loop to run the daemon and handle keyboard backlight patterns.'''
        last_mode = None
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

            if self.mode != last_mode:
                # Stop previous pattern thread if running
                if self.pattern_thread and self.pattern_thread.is_alive():
                    self.stop_pattern = True
                    self.pattern_thread.join()
                self.stop_pattern = False
                if self.mode == 'breathe':
                    self.pattern_thread = threading.Thread(target=self.breathe_pattern, daemon=True)
                    self.pattern_thread.start()
                elif self.mode == 'auto':
                    self.pattern_thread = threading.Thread(target=self.autobrightness_pattern, daemon=True)
                    self.pattern_thread.start()
                elif self.mode == 'responsive':
                    self.pattern_thread = threading.Thread(target=self.responsive_pattern, daemon=True)
                    self.pattern_thread.start()
                last_mode = self.mode
            time.sleep(0.2)

    def breathe_pattern(self):
        '''Run the breathing pattern for keyboard backlight.'''
        print('Running breathe pattern...')
        for i in range(0, 101):
            if getattr(self, 'stop_pattern', False):
                print('Breathe pattern stopped.')
                return
            self.set_brightness(i)
            time.sleep(0.03)
        for i in range(100, -1, -1):
            if getattr(self, 'stop_pattern', False):
                print('Breathe pattern stopped.')
                return
            self.set_brightness(i)
            time.sleep(0.03)

    def autobrightness_pattern(self):
        '''Run the auto brightness pattern based on ambient light.'''
        print('Running auto brightness pattern...')
        while not getattr(self, 'stop_pattern', False):
            self.set_brightness(50)
            time.sleep(1)

    def responsive_pattern(self):
        '''Run the responsive pattern based on keyboard input.'''
        print('Running responsive pattern...')
        timeout = 5  # seconds
        brightness_on = 100
        brightness_off = 0
        timer = None

        def turn_off():
            self.set_brightness(brightness_off)

        def reset_timer():
            nonlocal timer
            if timer:
                timer.cancel()
            timer = threading.Timer(timeout, turn_off)
            timer.start()

        devices = [InputDevice(path) for path in list_devices()]
        keyboard = None
        for device in devices:
            if 'keyboard' in device.name.lower():
                keyboard = device
                break
        if not keyboard:
            print('Keyboard device not found.')
            time.sleep(1)
            return

        self.set_brightness(brightness_off)
        reset_timer()
        try:
            for event in keyboard.read_loop():
                if getattr(self, 'stop_pattern', False):
                    print('Responsive pattern stopped.')
                    break
                if event.type == ecodes.EV_KEY:
                    key_event = categorize(event)
                    if key_event.keystate == key_event.key_down:
                        self.set_brightness(brightness_on)
                        reset_timer()
        except (OSError, IOError) as e:
            print(f"Device read error in responsive_pattern: {e}")
        except threading.ThreadError as e:
            print(f"Thread error in responsive_pattern: {e}")
        finally:
            if timer:
                timer.cancel()

    def set_brightness(self, value):
        '''Set the keyboard backlight brightness.'''

        try:
            subprocess.run(["pkexec", "/usr/bin/ectool", "pwmsetkblight", str(value)], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to set brightness: {e}")

    def start(self):
        '''Start the keyboard backlight daemon thread.'''

        self.thread = threading.Thread(target=self.run)
        self.thread.start()
        print('Keyboard backlight daemon started.')
        while self.running:
            time.sleep(1)

if __name__ == '__main__':
    daemon = KeyboardBacklightDaemon()
    daemon.start()
