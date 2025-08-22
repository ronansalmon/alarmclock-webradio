#
# Raspberry Pi Rotary Encoder Class
# $Id: rotary_class.py,v 1.4 2021/04/23 08:15:57 bob Exp $
#
# Author : Bob Rathbone
# Site   : http://www.bobrathbone.com
#
# This class uses standard rotary encoder with push switch
# git: https://github.com/bobrathbone/pirotary
#

import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class RotaryEncoder:

    CLOCKWISE=1
    ANTICLOCKWISE=2
    BUTTONDOWN=3
    BUTTONUP=4

    rotary_a = 0
    rotary_b = 0
    rotary_c = 0
    last_state = 0
    direction = 0
    button_laststate = 1
    polling_interval = 1 / 1000
    
    # Initialise rotary encoder object
    def __init__(self, pinA, pinB, button, callback):
        self.pinA = pinA
        self.pinB = pinB
        self.button = button
        self.callback = callback

        for pin, cb, bt, name  in [
          (self.pinA, self.switch_event, 30, "A"),
          (self.pinB, self.switch_event, 30, "B"),
          (self.button, self.button_event, 10, "BTN")
        ]:
          try:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Remove previous event detection if present (avoid RuntimeError)
            GPIO.remove_event_detect(pin)
            # Add event detection to the GPIO inputs
            GPIO.add_event_detect(pin, GPIO.BOTH, callback=cb, bouncetime=bt)
            print(f"add_event_detect ok for pin {pin} ({name})")
          except Exception as e:
            print(f"add_event_detect failed for pin {pin} ({name}): {e}")

    # Call back routine called by switch events
    def switch_event(self, switch):
        print("switch_event")
        if GPIO.input(self.pinA):
            self.rotary_a = 1
        else:
            self.rotary_a = 0

        if GPIO.input(self.pinB):
            self.rotary_b = 1
        else:
            self.rotary_b = 0

        self.rotary_c = self.rotary_a ^ self.rotary_b
        new_state = self.rotary_a * 4 + self.rotary_b * 2 + self.rotary_c * 1
        delta = (new_state - self.last_state) % 4
        self.last_state = new_state
        event = 0

        if delta == 1:
            if self.direction == self.CLOCKWISE:
                event = self.direction
            else:
                self.direction = self.CLOCKWISE
        elif delta == 3:
            if self.direction == self.ANTICLOCKWISE:
                event = self.direction
            else:
                self.direction = self.ANTICLOCKWISE
        if event > 0:
            self.callback(event)
        return

    # Push button up event
    def button_event(self, button):
        print("button_event")
        if GPIO.input(button):
            event = self.BUTTONUP
            self.button_laststate = 1
        else:
            if self.button_laststate == 0:
                event = self.BUTTONUP
                self.button_laststate = 1
            else:
                event = self.BUTTONDOWN 
                self.button_laststate = 0
        self.callback(event)
        return

    # Get a switch state
    def getSwitchState(self, switch):
        return GPIO.input(switch)

# End of RotaryEncoder class
