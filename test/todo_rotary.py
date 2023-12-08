#!/usr/bin/env python3      
import time      
import signal           
import sys
import RPi.GPIO as GPIO

BUTTON_GPIO = 5

start_time = 0

def signal_handler(sig, frame):
  GPIO.cleanup()
  sys.exit(0)

def button_callback(channel):
  global start_time

  if not GPIO.input(BUTTON_GPIO):
    print("Button pressed!")    
    start_time = time.time()
  else:
    buttonTime = time.time() - start_time

    if buttonTime >= .1:    # Ignore noise
      buttonStatus = 1    # 1= brief push

    if buttonTime >= 2:     
      buttonStatus = 2    # 2= Long push

    if buttonTime >= 4:
      buttonStatus = 3    # 3= really long push
    print("Button released!")
    print(buttonStatus)

if __name__ == '__main__':
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
  
  GPIO.add_event_detect(BUTTON_GPIO, GPIO.BOTH, callback=button_callback, bouncetime=50)
  
  signal.signal(signal.SIGINT, signal_handler)
  signal.pause()
