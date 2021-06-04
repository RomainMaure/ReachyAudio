"""This file comes from the manufacturer of the mic array.

It allows to control the LEDs of the microphone array.
"""

import usb.core
import usb.util


class PixelRing:
    TIMEOUT = 8000

    def __init__(self, dev):
        self.dev = dev

    def trace(self):
        self.write(0)

    def mono(self, color):
        self.write(1, [(color >> 16) & 0xFF, (color >> 8) & 0xFF, color & 0xFF, 0])
    
    def set_color(self, rgb=None, r=0, g=0, b=0):
        if rgb:
            self.mono(rgb)
        else:
            self.write(1, [r, g, b, 0])

    def off(self):
        self.mono(0)

    def listen(self, direction=None):
        self.write(2)

    def speak(self):
        self.write(3)

    def think(self):
        self.write(4)

    def spin(self):
        self.write(5)

    def show(self, data):
        self.write(6, data)
        
    def set_brightness(self, brightness):
        self.write(0x20, [brightness])
    
    def set_color_palette(self, a, b):
        self.write(0x21, [(a >> 16) & 0xFF, (a >> 8) & 0xFF, a & 0xFF, 0, (b >> 16) & 0xFF, (b >> 8) & 0xFF, b & 0xFF, 0])

    def set_vad_led(self, state):
        self.write(0x22, [state])

    def set_volume(self, volume):
        self.write(0x23, [volume])

    def change_pattern(self, pattern=None):
        print('Not support to change pattern')

    def write(self, cmd, data=[0]):
        self.dev.ctrl_transfer(
            usb.util.CTRL_OUT | usb.util.CTRL_TYPE_VENDOR | usb.util.CTRL_RECIPIENT_DEVICE,
            0, cmd, 0x1C, data, self.TIMEOUT)

    def close(self):
        """
        close the interface
        """
        usb.util.dispose_resources(self.dev)
