import configparser
import time
import json
import subprocess, os
import traceback
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import multiprocessing as mp
from rotary_class import RotaryEncoder
import RPi.GPIO as GPIO


client_id = "alarmclock_sound"
client_id_publish = "publish-oled"
topic_oled = "alarmclock_oled"
topic_sound = "alarmclock_sound"
app = None

class Radio():
  button_last_down = 0
  playlist = None
  start_time_sound = 0
  process = None
  default_volume = '0'

  def __init__(self):

    # default values
    config = configparser.ConfigParser()
    config.read('config.ini')
    self.default_volume = config['default']['sound_volume']

    rotary = RotaryEncoder(int(config['rotary_sound']['GPIO_DT']),int(config['rotary_sound']['GPIO_CLK']),int(config['rotary_sound']['GPIO_SW']), self.rotary_event)

    with open('media.json', 'r') as config_file:
      self.playlist = json.load(config_file)

    # init default volume
    os.system(f"amixer -q sset PCM '{self.default_volume}%'")
    print("Radio started")

  def __update_oled(self, msg):
    try:
      data = {"cmd": "media_text", "text": msg}
      publish.single(topic_oled, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    except Exception as e:
      traceback.print_exc()
      print(e)

  def thread_radio(self):
    try:
      print('Radio kickoff')

      media_index = 0
      errors = 0
      proc = subprocess.Popen(['ffplay', '-autoexit', '-nodisp', '-hide_banner', '-loglevel', 'error', self.playlist['medias'][media_index]['link']])
      self.__update_oled(self.playlist['medias'][media_index]['name'])

      # allow extra time to start since ffplay is slow to start
      time.sleep(3)
      while True:
        time.sleep(5)

        result = subprocess.check_output('grep RUNNING /proc/asound/card*/pcm*/sub*/status |wc -l', shell=True, text=True)
        state = int(result.strip())

        # make sure sound is coming out of player
        if state == 0:
          # player stopped or no music/radio is beeing played (netwok issue or remote server issue)!
          errors = errors + 1
        else:
          errors = 0
        
        # proc is dead
        if proc.poll() is not None:
          errors = 99

        # too many errors, swapping on next media
        if errors > 3:
          proc.terminate()
          errors = 0
          media_index = media_index + 1
          if media_index >= len(self.playlist['medias']):
            media_index = 0

          proc = subprocess.Popen(['ffplay', '-autoexit', '-nodisp', '-hide_banner', '-loglevel', 'error', self.playlist['medias'][media_index]['link']])
          self.__update_oled(self.playlist['medias'][media_index]['name'])
          # allow extra time to start since ffplay is slow to start
          time.sleep(3)

    except Exception as e:
      traceback.print_exc()
      print(e)
    finally:
      self.__update_oled("")
      proc.kill()
      os.system('killall -9 ffplay')

  def rotary_event(self, event):
    try:
      if event == RotaryEncoder.CLOCKWISE:
        os.system("amixer -q sset PCM '100%+'")
      elif event == RotaryEncoder.ANTICLOCKWISE:
        os.system("amixer -q sset PCM '100%-'")
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
        elif buttonTime > 0.5:
          # kill ffplay to move on the next available radio/file
          os.system('killall -9 ffplay')
        else:
          # simple push / toggle music
          if self.process is not None and self.process.is_alive():
            # stop music
            self.__update_oled("")
            self.process.terminate()
            self.process.join()
            self.process = None
            os.system('killall -9 ffplay')
          else:
            # start music
            self.process = mp.Process(target=self.thread_radio)
            self.process.start()
    except Exception as e:
      traceback.print_exc()
      print(e)
      
def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic=topic_sound)

def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"Subscribed with QoS {qos}")
  
def on_message(client, userdata, message, properties=None):
  global app
  try:
    payload = json.loads(message.payload)
    if payload['cmd'] == 'simple_push':
      app.rotary_event(RotaryEncoder.BUTTONDOWN)
      time.sleep(0.2)
      app.rotary_event(RotaryEncoder.BUTTONUP)
    elif payload['cmd'] == 'sound_off':
      os.system("amixer -q sset PCM '1%'")
    elif payload['cmd'] == 'sound_on':
      os.system(f"amixer -q sset PCM '{app.default_volume}%'")
    else:
      print(f"WTF! Topic: {message.topic}, payload: {payload}")
  except Exception as e:
    traceback.print_exc()
    print(e)


if __name__ == '__main__':
  app = None
  try:
    app = Radio()

    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.connect(host="127.0.0.1", port=1883, keepalive=60)

    client.loop_forever()
  except Exception as e:
    if app is not None and app.process is not None:
      app.process.terminate()
      app.process.join()
    traceback.print_exc()
    print(e)
  finally:
    GPIO.cleanup()
    
  app = Radio()


