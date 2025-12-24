from rotary import RotaryEncoder

import time

def menu_up():
    print("menu_up")

def menu_down():
    print("menu_down")

def selected(event):
    print("Button selected")

def setVolume(count):
    print(f"setVolume {count}")
    
def mute(event):
    print("Button mute")

## Setup First Encoder
# arguments: (clk,dt,sw,tck)

menu_encoder = RotaryEncoder(13,6,5,2)
menu_encoder.register(increment=menu_up,decrement=menu_down,pressed=selected)
menu_encoder.start()
time.sleep(60)
menu_encoder.stop()


## Setup Second Encoder
#volume_encoder = rotary.Rotary(22,27,17,1)
#volume_encoder.register(onchange=setVolume,pressed=mute)
#volume_encoder.start()
