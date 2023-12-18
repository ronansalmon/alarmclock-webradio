import sys
import time
from rotary_class import RotaryEncoder

# Define GPIO inputs
PIN_A = 27
PIN_B = 22
BUTTON = 17

clockwise_time = 0
tick_count = 0
anticlockwise_time = 0

# This is the event callback routine to handle events
def switch_event(event):
  global clockwise_time, tick_count, anticlockwise_time

  if event == RotaryEncoder.CLOCKWISE:
    if anticlockwise_time != 0:
      # changed direction
      clockwise_time = time.time()
      anticlockwise_time = 0
      tick_count = 0
      print(f"Clockwise {clockwise_time}")
    else:
      if clockwise_time != 0:
        # not the first time
        tickTime = time.time() - clockwise_time
        clockwise_time = time.time()
        if tickTime <= .05:
          tick_count = tick_count + 1
        else:
          tick_count = 1
        
        if tick_count <5:
          print(f"Clockwise tickTime {tickTime}")
        elif tick_count <10:
          print(f"Double Clockwise {tickTime}")
        else:
          print(f"Bigger Clockwise {tickTime}")
      else:
        clockwise_time = time.time()
        anticlockwise_time = 0
        tick_count = 0
        tick_count = 0
        print(f"Clockwise {clockwise_time}")
      
  elif event == RotaryEncoder.ANTICLOCKWISE:
    if clockwise_time != 0:
      # changed direction
      anticlockwise_time = time.time()
      clockwise_time = 0
      tick_count = 0
      print(f"Anticlockwise {clockwise_time}")
    else:
      if anticlockwise_time != 0:
        # not the first time
        tickTime = time.time() - anticlockwise_time
        anticlockwise_time = time.time()
        if tickTime <= .05:
          tick_count = tick_count + 1
        else:
          tick_count = 1
        
        if tick_count <5:
          print(f"Anticlockwise tickTime {tickTime}")
        elif tick_count <10:
          print(f"Double Anticlockwise {tickTime}")
        else:
          print(f"Bigger Anticlockwise {tickTime}")
      else:
        anticlockwise_time = time.time()
        clockwise_time = 0
        tick_count = 0
        tick_count = 0
        print(f"Anticlockwise {clockwise_time}")
  elif event == RotaryEncoder.BUTTONDOWN:
    clockwise_time = 0
    anticlockwise_time = 0
    print("Button down")
  elif event == RotaryEncoder.BUTTONUP:
    print("Button up")
  return

# Define the switch
rswitch = RotaryEncoder(PIN_A,PIN_B,BUTTON,switch_event)

print("Pin A "+ str(PIN_A))
print("Pin B "+ str(PIN_B))
print("BUTTON "+ str(BUTTON))

# Listen
while True:
  time.sleep(0.5)


