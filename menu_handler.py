import configparser
import time
import json
import traceback
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import multiprocessing as mp
import os.path
import shutil
from datetime import datetime
from time import strftime
from time import gmtime

client_id = "alarmclock_menu"
client_id_publish = "publish-rotary-menu"
topic_sound = "alarmclock_sound"
topic_menu = "alarmclock_menu"
topic_oled = "alarmclock_oled"
process = None
mode = 0
alarm_time = 0

def update_oled(msg):
  try:
    data = {"cmd": "alarm_text", "text": msg}
    publish.single(topic_oled, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id_publish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")

  except Exception as e:
    traceback.print_exc()
    print(e)


def thread_alarm():
  try:
    # we must read config everytime to get an uptodate version
    config = configparser.ConfigParser()
    config.read('config.ini')
    alarm = int(config['alarm']['alarm_time'])
    now = datetime.now()
    sleep = 0
    seconds_so_far = now.hour * 3600 + now.minute * 60  + now.second
    alarm_str = strftime("%H:%M", gmtime(alarm))
    print(f"Alarm set to '{alarm_str}'")

    if seconds_so_far > alarm:
      sleep = alarm + (24 * 3600 - seconds_so_far)
    else:
      sleep = alarm - seconds_so_far

    # sanity check
    if sleep < 1:
      sleep = 1
      
    print(f"Sleeping for {sleep} seconds")
    time.sleep(sleep)
    # time to wakeup now !
    
    data = {"cmd": "simple_push"}
    publish.single(topic_sound, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_idpublish, keepalive=60, will=None, auth=None, tls=None, transport="tcp")
    
  except Exception as e:
    traceback.print_exc()
    print(e)

def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic=topic_menu)

def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"Subscribed with QoS {qos}")

def on_message(client, userdata, message, properties=None):
  global process, mode, alarm_time
  try:
    payload = json.loads(message.payload)
    
    print(payload)
    print(mode)
    
    if payload['cmd'] == 'decrease':
      # TODO: must update oled
      if mode == 1:
        alarm_time - 60
        update_oled(time.strftime("%H:%M", time.gmtime(alarm_time)) + " #")
        
    elif payload['cmd'] == 'increase':
      # TODO: must update oled
      if mode == 1:
        alarm_time + 60
        update_oled(time.strftime("%H:%M", time.gmtime(alarm_time)) + " #")

    elif payload['cmd'] == 'simple_push':
      # toggle alarm on/off
      # and may need to leave setup mode

      # TODO: must update oled

      if mode == 1:
        # leaving setup mode, we must save the new settings
        config['alarm']['alarm_time'] = alarm_time
        with open('config.ini', 'w') as configfile:
          config.write(configfile)
        mode = 0

      if process is not None and process.is_alive():
        # stop music
        update_oled("")
        process.terminate()
        process.join()
        process = None
      else:
        # start music
        process = mp.Process(target=thread_alarm)
        process.start()
        update_oled(time.strftime("%H:%M", time.gmtime(alarm_time)))

    elif payload['cmd'] == 'long_push':
      mode = 1
      # disable alarm. user will have to enable it again after setting new time
      if process is not None and process.is_alive():
        # stop music
        process.terminate()
        process.join()
        process = None
        update_oled(time.strftime("%H:%M", time.gmtime(alarm_time)) + " #")
    else:
      print(f"WTF! Topic: {message.topic}, payload: {payload}")

  except Exception as e:
    traceback.print_exc()
    print(e)


if __name__ == '__main__':
  try:
    # default config file
    if os.path.exists('config.ini') == False:
      shutil.copy('config.ini.default', 'config.ini')
      
    config = configparser.ConfigParser()
    config.read('config.ini')
    print("Menu Handler Started")
    alarm_time = int(config['alarm']['alarm_time'])
    alarm_enable = config.getboolean('alarm','alarm_enable')

    if alarm_enable:
      process = mp.Process(target=thread_alarm)
      process.start()
      update_oled(time.strftime("%H:%M", time.gmtime(alarm_time)))
    
    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    client.connect(host="127.0.0.1", port=1883, keepalive=60)
    
    client.loop_forever()

  except Exception as e:
    if process is not None:
      process.terminate()
      process.join()
    traceback.print_exc()
    print(e)

