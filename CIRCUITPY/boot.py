# SPDX-FileCopyrightText: 2017 Limor Fried for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials Storage logging boot.py file"""
import board
# import digitalio
import storage
import analogio

# For Gemma M0, Trinket M0, Metro M0/M4 Express, ItsyBitsy M0/M4 Express
# switch = digitalio.DigitalInOut(board.D2)

# For Feather M0/M4 Express
# switch = digitalio.DigitalInOut(board.D5)

# For Circuit Playground Express, Circuit Playground Bluefruit
# switch = digitalio.DigitalInOut(board.D7)

# switch.direction = digitalio.Direction.INPUT
# switch.pull = digitalio.Pull.UP

usbpin = analogio.AnalogIn(board.A2)
v = usbpin.value
if v < 35000: 
    storage.remount("/", readonly=False)
    print ("usbpin = {} - Flash remounted R/W".format(v))
else:
    print ("usbpin = {} - Flash readonly".format(v))
    


