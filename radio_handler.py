import configparser
import time
import json
import subprocess, os
import traceback
import paho.mqtt.client as mqtt
import multiprocessing as mp

process = None

def thread_radio():
  try:
    print('Radio kickoff')
    with open('media.json', 'r') as config_file:
      medias_list = json.load(config_file)

    media_index = 0
    errors = 0
    proc = subprocess.Popen(['ffplay', '-nodisp', '-hide_banner', '-loglevel', 'error', medias_list['medias'][media_index]['link']])
    print(medias_list['medias'][media_index]['name'])
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
        if media_index >= len(medias_list):
          media_index = 0

        proc = subprocess.Popen(['ffplay', '-nodisp', '-hide_banner', '-loglevel', 'error', medias_list['medias'][media_index]['link']])
        print(medias_list['medias'][media_index]['name'])
        # allow extra time to start since ffplay is slow to start
        time.sleep(3)

  except Exception as e:
    traceback.print_exc()
    print(e)
  finally:
    proc.kill()
    os.system('killall -9 ffplay')


def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic="alarmclock_sound")

def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"Subscribed with QoS {qos}")

def on_message(client, userdata, message, properties=None):
  global process
  try:
    payload = json.loads(message.payload)
    if payload['cmd'] == 'decrease':
      os.system("amixer -q sset PCM '100%-'")
    elif payload['cmd'] == 'increase':
      os.system("amixer -q sset PCM '100%+'")
    elif payload['cmd'] == 'setvolume':
      try:
        volume = int(payload['volume'])
      except:
        volume = 90
      os.system(f"amixer -q sset PCM '{volume}%'")
    elif payload['cmd'] == 'simple_push':
      if process.is_alive():
        # stop music
        process.terminate()
        process.join()
        os.system('killall -9 ffplay')
      else:
        # start music
        process.start()
    elif payload['cmd'] == 'long_push':
        # kill ffplay to move on the next available radio/file
        os.system('killall -9 ffplay')
    else:
      print(f"WTF! Topic: {message.topic}, payload: {payload}")

  except Exception as e:
    traceback.print_exc()
    print(e)


if __name__ == '__main__':
  try:
    config = configparser.ConfigParser()
    config.read('config.ini')

    # init default volume
    os.system(f"amixer -q sset PCM '{config['default']['sound_volume']}%'")
    process = mp.Process(target=thread_radio)
    
    client = mqtt.Client(client_id="alarmclock_radio", protocol=mqtt.MQTTv311, clean_session=True)
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

