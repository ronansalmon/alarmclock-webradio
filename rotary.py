#
# Raspberry Pi Rotary Encoder Class
# based on https://github.com/AllanGallop/RPi_GPIO_Rotary/

from RPi import GPIO
import threading, time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class RotaryEncoder:
    CLOCKWISE=1
    ANTICLOCKWISE=2
    BUTTONDOWN=3
    BUTTONUP=4
    button_laststate = 0
    
    def setup(self):
    
        try:
          GPIO.setup(self.pins['clk'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(self.pins['dt'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
          GPIO.setup(self.pins['sw'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
          # Remove previous event detection if present (avoid RuntimeError)
          GPIO.remove_event_detect(self.pins['clk'])
          GPIO.remove_event_detect(self.pins['dt'])
          GPIO.remove_event_detect(self.pins['sw'])

          # Add event detection to the GPIO inputs
          GPIO.add_event_detect(self.pins['sw'], GPIO.BOTH, callback=self.button_event, bouncetime=10)
        except Exception as e:
          print(f"add_event_detect failed for pin {self.pins['sw']}: {e}")

    def __init__(self,clk = None,dt = None,sw = None, tick = 2, bounce=500):
        if not clk or not dt or not sw:
            raise BaseException("Invalid Configuration: CLK, DT and SW must be specified")
        self.pins = {"clk":clk,"dt":dt,"sw":sw}
        self.ticks = tick
        self.bounce = bounce
        self.increment, self.decrement, self.switched, self.changed = None,None,None,None
        self.setup()


    def register(self, **params):
        if 'increment' in params:
            self.increment= params['increment']
        if 'decrement' in params:
            self.decrement = params['decrement']
        if 'pressed' in params:
            self.switched = params['pressed']
        if 'onchange' in params:
            self.changed= params['onchange'] 

    # Push button up event
    def button_event(self, button):
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
        self.switched(event)
        return


    def watch(self, stop_event):
        clkLastState = GPIO.input(self.pins['clk'])
        counter = 0
        tick = 1
        pressed = 0
        button_laststate = 0
        
        while not stop_event.is_set():
            clkState = GPIO.input(self.pins['clk'])
            dtState = GPIO.input(self.pins['dt'])

            if clkState != clkLastState:
                if tick == self.ticks:
                    tick =1
                    if dtState != clkState:
                        counter += 1
                        if self.increment is not None:
                            self.increment()
                    elif dtState == clkState:
                        counter -= 1
                        if self.decrement is not None:
                            self.decrement()
                    if self.changed is not None:
                        self.changed(counter)
                else:
                    tick += 1
            clkLastState = clkState
            time.sleep(0.0025)

    def start(self):
        self.stop_event = threading.Event()
        self.th = threading.Thread(target=self.watch, args=[self.stop_event])
        self.th.setDaemon(True)
        self.th.start()
    
    def stop(self):
        self.stop_event.set()
