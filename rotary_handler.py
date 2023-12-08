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
start_time = 0
gpio_callback_sound = 0
gpio_callback_menu = 0

def button_callback_sound(channel):
  global start_time, button_callback_sound

  if not GPIO.input(gpio_callback_sound):
    start_time = time.time()
  else:
    buttonTime = time.time() - start_time

    if buttonTime >= 2:
      # Long push
      data = {"cmd": "long_push"}
    elif buttonTime <= .01:
      # Ignore noise
      return
    else:
      # simple push
      data = {"cmd": "simple_push"}
    try:
      publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    except:
      pass
      
def button_callback_menu(channel):
  global start_time, gpio_callback_menu

  if not GPIO.input(gpio_callback_menu):
    start_time = time.time()
  else:
    buttonTime = time.time() - start_time

    if buttonTime >= 2:
      # Long push
      data = {"cmd": "long_push"}
    elif buttonTime <= .01:
      # Ignore noise
      return
    else:
      # simple push
      data = {"cmd": "simple_push"}
    try:
      publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    except:
      pass

def dec_callback_sound(scale_position):
  data = {"cmd": "decrease"}
  try:
    publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

def inc_callback_sound(scale_position):
  data = {"cmd": "increase"}
  try:
    publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

  
def dec_callback_menu(scale_position):
  data = {"menu": "decrease"}
  try:
    publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

def inc_callback_menu(scale_position):
  data = {"menu": "increase"}
  try:
    publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass
def click_menu():
  data = {"menu": "click"}
  try:
    publish.single(topic_menu, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
  except:
    pass

if __name__ == '__main__':
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    gpio_callback_sound = int(config['rotary_sound']['GPIO_SW'])
    gpio_callback_menu = int(config['rotary_menu']['GPIO_SW'])
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(gpio_callback_sound, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(gpio_callback_menu, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(gpio_callback_sound, GPIO.BOTH, callback=button_callback_sound, bouncetime=50)
    GPIO.add_event_detect(gpio_callback_menu, GPIO.BOTH, callback=button_callback_menu, bouncetime=50)
    
    rotary_sound = pyky040.Encoder(CLK=int(config['rotary_sound']['GPIO_CLK']), DT=int(config['rotary_sound']['GPIO_DT']))
    rotary_sound.setup(scale_min=0, scale_max=100, step=1, inc_callback=inc_callback_sound, dec_callback=dec_callback_sound)

    rotary_menu = pyky040.Encoder(CLK=int(config['rotary_menu']['GPIO_CLK']), DT=int(config['rotary_menu']['GPIO_DT']), SW=int(config['rotary_menu']['GPIO_SW']))
    rotary_menu.setup(scale_min=0, scale_max=100, step=1, inc_callback=inc_callback_menu, dec_callback=dec_callback_menu)

    thread_sound = threading.Thread(target=rotary_sound.watch)
    thread_menu = threading.Thread(target=rotary_menu.watch)

    # Launch the thread
    thread_sound.start()
    thread_menu.start()
    print('Started...')
  except(KeyboardInterrupt):
    if thread_sound is not None:
      thread_sound.terminate()
      thread_sound.join()
    if thread_menu is not None:
      thread_menu.terminate()
      thread_menu.join()

