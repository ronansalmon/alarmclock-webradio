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
  clockwise_time = 0
  tick_count = 0
  anticlockwise_time = 0
  ignore_ads = 0

  def __init__(self):

    # default values
    self.config = configparser.ConfigParser()
    self.config.read('config.ini')
    self.alarm_time = int(self.config['alarm']['alarm_time'])
    self.alarm_enable = self.config.getboolean('alarm','alarm_enable')
    self.ignore_ads = int(self.config['alarm']['ignore_ads'])

    if self.alarm_enable:
      self.process = mp.Process(target=self.thread_alarm)
      self.process.start()
      self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)))

    rotary = RotaryEncoder(int(self.config['rotary_menu']['GPIO_DT']),int(self.config['rotary_menu']['GPIO_CLK']),int(self.config['rotary_menu']['GPIO_SW']), self.rotary_event)
    print("Menu Handler Started")

  def __update_oled(self, msg, cmd="alarm_text"):
    try:
      data = {"cmd": cmd, "text": msg}
      publish.single(topic_oled, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")

    except Exception as e:
      traceback.print_exc()
      print(e)

  def thread_alarm(self):
    try:
      # everyday !
      while True:
        # we must read config everytime to get an uptodate version
        self.config.read('config.ini')
        alarm = int(self.config['alarm']['alarm_time'])
        now = datetime.now()
        sleep = 0
        seconds_so_far = now.hour * 3600 + now.minute * 60  + now.second
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
        publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")

        if self.ignore_ads != 0:
          # quiet down to silently play ads on webradio connect
          data = {"cmd": "sound_off"}
          publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
          time.sleep(self.ignore_ads)
          data = {"cmd": "sound_on"}
          publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")

        # wait for a few secondes : alarm != now
        time.sleep(5)

    except Exception as e:
      traceback.print_exc()
      print(e)

  def rotary_event(self, event):
    try:
      if event == RotaryEncoder.CLOCKWISE:
        if self.anticlockwise_time != 0:
          # changed direction
          self.clockwise_time = time.time()
          self.anticlockwise_time = 0
          self.tick_count = 0
          if self.mode == 1:
            self.alarm_time = self.alarm_time + 60
            self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
        else:
          if self.clockwise_time != 0:
            # not the first time
            tickTime = time.time() - self.clockwise_time
            self.clockwise_time = time.time()
            if tickTime <= .05:
              self.tick_count = self.tick_count + 1
            else:
              self.tick_count = 1

            if self.tick_count <5:
              if self.mode == 1:
                self.alarm_time = self.alarm_time + 60
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
            elif self.tick_count <10:
              if self.mode == 1:
                self.alarm_time = self.alarm_time + 600
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
            else:
              if self.mode == 1:
                self.alarm_time = self.alarm_time + 3600
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
          else:
            self.clockwise_time = time.time()
            self.anticlockwise_time = 0
            self.tick_count = 0
            self.tick_count = 0

      elif event == RotaryEncoder.ANTICLOCKWISE:
        if self.clockwise_time != 0:
          # changed direction
          self.anticlockwise_time = time.time()
          self.clockwise_time = 0
          self.tick_count = 0
          if self.mode == 1:
            self.alarm_time = self.alarm_time - 60
            self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
        else:
          if self.anticlockwise_time != 0:
            # not the first time
            tickTime = time.time() - self.anticlockwise_time
            self.anticlockwise_time = time.time()
            if tickTime <= .05:
              self.tick_count = self.tick_count + 1
            else:
              self.tick_count = 1

            if self.tick_count <5:
              if self.mode == 1:
                self.alarm_time = self.alarm_time - 60
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
            elif self.tick_count <10:
              if self.mode == 1:
                self.alarm_time = self.alarm_time - 600
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
            else:
              if self.mode == 1:
                self.alarm_time = self.alarm_time - 3600
                self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")
          else:
            self.anticlockwise_time = time.time()
            self.clockwise_time = 0
            self.tick_count = 0
            self.tick_count = 0
            if self.mode == 1:
              self.alarm_time = self.alarm_time - 60
              self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")

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
          # mode alarm setup
          self.mode = 1
          self.__update_oled(0.4, "alarm_setup")

          # disable alarm. user will have to enable it again after setting new time
          if self.process is not None and self.process.is_alive():
            # stop music
            self.process.terminate()
            self.process.join()
            self.process = None
            self.__update_oled(time.strftime("%H:%M", time.gmtime(self.alarm_time)) + " #")

        else:
          # simple push
          # toggle alarm on/off
          # and may need to leave setup mode

          if self.mode == 1:
            # leaving setup mode, we must save the new settings
            # make sure that alarm_time's day is today !
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
            # stop alarm
            self.config['alarm']['alarm_enable'] = "False"
            with open('config.ini', 'w') as configfile:
              self.config.write(configfile)
            
            self.__update_oled("")
            self.process.terminate()
            self.process.join()
            self.process = None
          else:
            # start alarm
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
  try:
    # default config file
    if os.path.exists('config.ini') == False:
      shutil.copy('config.ini.default', 'config.ini')
      
    app = Menu()
    while True:
      time.sleep(0.5)
  except Exception as e:
    if app.process is not None:
      app.process.terminate()
      app.process.join()
    traceback.print_exc()
    print(e)

