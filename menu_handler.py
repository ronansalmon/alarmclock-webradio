import configparser
import time
import json
import traceback
import paho.mqtt.publish as publish
import multiprocessing as mp
import threading
import os.path
import shutil
from datetime import datetime
from datetime import timedelta
from rotary_class import RotaryEncoder
import RPi.GPIO as GPIO

client_id_publish = "publish-rotary-menu"
topic_sound = "alarmclock_sound"
topic_oled = "alarmclock_oled"

class Menu():
  button_last_down = 0
  start_time_menu = 0
  process = None
  mode = 0
  alarm_time = 0
  alarm_enable = False
  ignore_ads = 0
  
  # New rotary handling variables
  last_rotary_time = 0
  last_rotary_direction = None
  pending_timer = None
  rotation_count = 0

  def __init__(self):
    # default values
    self.config = configparser.ConfigParser()
    self.config.read('config.ini')
    self.alarm_time = int(self.config['alarm']['alarm_time'])
    self.alarm_enable = self.config.getboolean('alarm', 'alarm_enable')
    self.ignore_ads = int(self.config['alarm']['ignore_ads'])

    if self.alarm_enable:
      self.process = mp.Process(target=self.thread_alarm)
      self.process.start()
      self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)))

    rotary = RotaryEncoder(
      int(self.config['rotary_menu']['GPIO_DT']),
      int(self.config['rotary_menu']['GPIO_CLK']),
      int(self.config['rotary_menu']['GPIO_SW']),
      self.rotary_event
    )
    print("Menu Handler Started")

  def __update_oled(self, msg, cmd="alarm_text"):
    try:
      data = {"cmd": cmd, "text": msg}
      publish.single(topic_oled, payload=json.dumps(data), retain=False,
        hostname="127.0.0.1", port=1883, client_id=client_id_publish,
        keepalive=60, will=None, auth=None, tls=None, transport="tcp")

    except Exception as e:
      traceback.print_exc()
      print(e)

  def thread_alarm(self):
    try:
      # everyday !
      while True:
        # we must read config everytime to get an uptodate version
        self.config.read('config.ini')
        alarm = int(self.config['alarm']['alarm_time'])
        now = datetime.now()
        sleep = 0
        seconds_so_far = now.hour * 3600 + now.minute * 60 + now.second
        alarm_str = time.strftime("%H:%M", time.gmtime(alarm))
        print(f"Alarm set to '{alarm_str}'")

        if seconds_so_far > alarm:
          sleep = alarm + (24 * 3600 - seconds_so_far)
        else:
          sleep = alarm - seconds_so_far

        if self.ignore_ads != 0:
          sleep -= self.ignore_ads

        # sanity check
        if sleep < 1:
          sleep = 1

        print(f"Sleeping for {sleep} seconds")
        time.sleep(sleep)
        # time to wakeup now !

        data = {"cmd": "simple_push"}
        publish.single(topic_sound, payload=json.dumps(data), retain=False,
                 hostname="127.0.0.1", port=1883, client_id=client_id_publish,
                 keepalive=60, will=None, auth=None, tls=None, transport="tcp")

        if self.ignore_ads != 0:
          # quiet down to silently play ads on webradio connect
          data = {"cmd": "sound_off"}
          publish.single(topic_sound, payload=json.dumps(data), retain=False,
                   hostname="127.0.0.1", port=1883, client_id=client_id_publish,
                   keepalive=60, will=None, auth=None, tls=None, transport="tcp")
          time.sleep(self.ignore_ads)
          data = {"cmd": "sound_on"}
          publish.single(topic_sound, payload=json.dumps(data), retain=False,
                   hostname="127.0.0.1", port=1883, client_id=client_id_publish,
                   keepalive=60, will=None, auth=None, tls=None, transport="tcp")

        # wait for a few seconds: alarm != now
        time.sleep(5)

    except Exception as e:
      traceback.print_exc()
      print(e)

  def process_accumulated_rotation(self):
    """Process the accumulated rotations after a short delay"""
    if self.mode == 1 and self.last_rotary_direction is not None:
      # Determine increment based on rotation speed
      # Un cran physique génère généralement 1-4 événements
      if self.rotation_count <= 4:
        increment = 60
        speed_desc = "slow"
      elif self.rotation_count <= 12:
        increment = 600  
        speed_desc = "medium"
      else:
        increment = 3600
        speed_desc = "fast"
      
      if self.last_rotary_direction == RotaryEncoder.CLOCKWISE:
        print(f"+{increment}s ({speed_desc}, {self.rotation_count} events)")
        self.alarm_time = self.alarm_time + increment
      else:
        print(f"-{increment}s ({speed_desc}, {self.rotation_count} events)")
        self.alarm_time = self.alarm_time - increment
      
      self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
    
    # Reset for next rotation
    self.rotation_count = 0
    self.last_rotary_direction = None
    self.pending_timer = None

  def rotary_event(self, event):
    try:
      current_time = time.time()
      
      if event in [RotaryEncoder.CLOCKWISE, RotaryEncoder.ANTICLOCKWISE]:
        # Cancel any pending timer
        if self.pending_timer is not None:
          self.pending_timer.cancel()
        
        # If this is the first rotation or same direction as before
        if (self.last_rotary_direction is None or 
            self.last_rotary_direction == event or 
            current_time - self.last_rotary_time > 0.3):
          
          # Reset if direction changed or too much time passed
          if (self.last_rotary_direction is not None and 
              self.last_rotary_direction != event):
            print(f"Direction changed from {'CW' if self.last_rotary_direction == RotaryEncoder.CLOCKWISE else 'CCW'} to {'CW' if event == RotaryEncoder.CLOCKWISE else 'CCW'}")
            self.rotation_count = 0
          
          # If it's been too long since last rotation, reset count
          if current_time - self.last_rotary_time > 0.3:
            self.rotation_count = 0
          
          self.last_rotary_direction = event
          self.rotation_count += 1
          self.last_rotary_time = current_time
          
          print(f"Rotation {'CW' if event == RotaryEncoder.CLOCKWISE else 'CCW'} #{self.rotation_count}")
          
          # Start a timer to process the rotation after a short delay
          # This allows multiple rapid events to accumulate
          self.pending_timer = threading.Timer(0.2, self.process_accumulated_rotation)
          self.pending_timer.start()

      elif event == RotaryEncoder.BUTTONDOWN:
        self.button_last_down = time.time()
      elif event == RotaryEncoder.BUTTONUP:

        if self.button_last_down == 0:
          # Ignore noise
          return

        buttonTime = time.time() - self.button_last_down
        self.button_last_down = 0

        if buttonTime <= .01:
          # Ignore noise
          return
        elif buttonTime > 1:
          # mode alarm setup
          self.mode = 1
          self.__update_oled(0.4, "alarm_setup")

          # disable alarm. user will have to enable it again after setting new time
          if self.process is not None and self.process.is_alive():
            # stop music
            self.process.terminate()
            self.process.join()
            self.process = None
            self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")

        else:
          # simple push
          # toggle alarm on/off
          # and may need to leave setup mode

          if self.mode == 1:
            # leaving setup mode, we must save the new settings
            # make sure that alarm_time's day is today !
            delta = timedelta(
              minutes=int(time.strftime("%M", time.gmtime(self.alarm_time))),
              hours=int(time.strftime("%H", time.gmtime(self.alarm_time)))
            )
            self.alarm_time = int(delta.total_seconds())
            self.config['alarm']['alarm_time'] = str(self.alarm_time)
            with open('config.ini', 'w') as configfile:
              self.config.write(configfile)
            self.mode = 0
            self.__update_oled(int(self.config['oled']['auto_refresh']), "alarm_setup")

          if self.process is not None and self.process.is_alive():
            # stop alarm
            self.config['alarm']['alarm_enable'] = "False"
            with open('config.ini', 'w') as configfile:
              self.config.write(configfile)

            self.__update_oled("")
            self.process.terminate()
            self.process.join()
            self.process = None
          else:
            # start alarm
            self.config['alarm']['alarm_enable'] = "True"
            with open('config.ini', 'w') as configfile:
              self.config.write(configfile)

            self.process = mp.Process(target=self.thread_alarm)
            self.process.start()
            self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)))

    except Exception as e:
      traceback.print_exc()
      print(e)

if __name__ == '__main__':
  app = None
  try:
    # default config file
    if not os.path.exists('config.ini'):
      shutil.copy('config.ini.default', 'config.ini')

    app = Menu()
    while True:
      time.sleep(0.5)
  except Exception as e:
    if app is not None and app.process is not None:
      app.process.terminate()
      app.process.join()
    traceback.print_exc()
    print(e)
  finally:
    GPIO.cleanup()
