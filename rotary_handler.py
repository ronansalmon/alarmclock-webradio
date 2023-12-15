import paho.mqtt.publish as publish
import random
import time
import json
import threading
import configparser
import RPi.GPIO as GPIO
from pyky040 import pyky040

client_id = "publish-rotary-sound"
topic_sound = "alarmclock_sound"
topic_menu = "alarmclock_menu"
start_time_sound = 0
start_time_menu = 0
gpio_callback_sound = 0
gpio_callback_menu = 0

def button_callback_sound(channel):
  global start_time_sound
  if not GPIO.input(channel):
    start_time_sound = time.time()
  else:
    buttonTime = time.time() - start_time_sound
  
    if buttonTime <= .01:
      # Ignore noise
      return
    elif buttonTime > 0.5:
      if buttonTime < 2:
        # short push
        data = {"cmd": "short_push"}
      else:
        # long push
        data = {"cmd": "long_push"}
    else:
      # simple push
      data = {"cmd": "simple_push"}
    try:
      print(f"topic: {topic_sound}, data: {data}")
      publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    except:
      pass
      
def button_callback_menu(channel):
  global start_time_menu
  if not GPIO.input(channel):
    start_time_menu = time.time()
  else:
    buttonTime = time.time() - start_time_menu
  
    if buttonTime <= .01:
      # Ignore noise
      return
    elif buttonTime > 0.5:
      if buttonTime < 2:
        # short push
        data = {"cmd": "short_push"}
      else:
        # long push
        data = {"cmd": "long_push"}
    else:
      # simple push
      data = {"cmd": "simple_push"}
    try:
      print(f"topic: {topic_menu}, data: {data}")
      publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    except:
      pass

def dec_callback_sound(scale_position):
  try:
    data = {"cmd": "decrease"}
    print(f"topic: {topic_sound}, data: {data}")
    publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

def inc_callback_sound(scale_position):
  try:
    data = {"cmd": "increase"}
    print(f"topic: {topic_sound}, data: {data}")
    publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

def dec_callback_menu(scale_position):
  try:
    data = {"cmd": "decrease"}
    print(f"topic: {topic_menu}, data: {data}")
    publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

def inc_callback_menu(scale_position):
  try:
    data = {"cmd": "increase"}
    print(f"topic: {topic_menu}, data: {data}")
    publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

if __name__ == '__main__':
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')

    rotary_sound = pyky040.Encoder(CLK=int(config['rotary_sound']['GPIO_CLK']), DT=int(config['rotary_sound']['GPIO_DT']))
    rotary_menu  = pyky040.Encoder(CLK=int(config['rotary_menu']['GPIO_CLK']) , DT=int(config['rotary_menu']['GPIO_DT']))
    rotary_sound.setup(inc_callback=inc_callback_sound, dec_callback=dec_callback_sound)
    rotary_menu.setup(inc_callback=inc_callback_menu, dec_callback=dec_callback_menu)
    thread_sound = threading.Thread(target=rotary_sound.watch)
    thread_menu  = threading.Thread(target=rotary_menu.watch)

    # Launch the thread
    thread_sound.start()
    thread_menu.start()


    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    gpio_callback_sound = int(config['rotary_sound']['GPIO_SW'])
    gpio_callback_menu  = int(config['rotary_menu']['GPIO_SW'])
    GPIO.setup(gpio_callback_sound, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(gpio_callback_menu , GPIO.IN, pull_up_down=GPIO.PUD_UP)
    
    GPIO.add_event_detect(gpio_callback_sound, GPIO.BOTH, callback=button_callback_sound, bouncetime=50)
    GPIO.add_event_detect(gpio_callback_menu , GPIO.BOTH, callback=button_callback_menu , bouncetime=50)
    
    print('Started...')
  except(KeyboardInterrupt):
    if thread_sound is not None:
      thread_sound.terminate()
      thread_sound.join()
    if thread_menu is not None:
      thread_menu.terminate()
      thread_menu.join()

