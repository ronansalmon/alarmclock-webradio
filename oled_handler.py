import configparser
import time
import json
import subprocess, os
import traceback
import paho.mqtt.client as mqtt
import multiprocessing as mp

process = None

def thread_oled():
  try:
    print('Oled kickoff')

    while True:
      time.sleep(5)
      print('TODO')

  except Exception as e:
    traceback.print_exc()
    print(e)

def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic="alarmclock_oled")

def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"Subscribed with QoS {qos}")

def on_message(client, userdata, message, properties=None):
  global process
  try:
    payload = json.loads(message.payload)
    if payload['cmd'] == 'toggle_alarm':

    elif payload['cmd'] == 'todo':
        print('TODO')
    else:
      print(f"WTF! Topic: {message.topic}, payload: {payload}")

  except Exception as e:
    traceback.print_exc()
    print(e)


if __name__ == '__main__':
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')
    alarm_enable = config.getboolean('alarm','alarm_enable')
    alarm_time = config['alarm']['alarm_time']


    client = mqtt.Client(client_id="alarmclock_menu", protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.connect(host="127.0.0.1", port=1883, keepalive=60)
    
    client.loop_forever()

  except Exception as e:
    if process is not None:
      process.terminate()
      process.join()
    os.system('killall -9 ffplay')
    traceback.print_exc()
    print(e)

