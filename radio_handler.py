import configparser
import time
import json
import subprocess, os
import traceback
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import multiprocessing as mp

process = None
client_id = "publish-oled"
topic_oled = "alarmclock_oled"

def update_oled(msg):
  try:
    data = {"cmd": "media_text", "text": msg}
    publish.single(topic_oled, payload=json.dumps(data), retain=False, hostname="127.0.0.1", port=1883, client_id=client_id, keepalive=60, will=None, auth=None, tls=None, transport="tcp")

  except Exception as e:
    traceback.print_exc()
    print(e)

def thread_radio():
  try:
    print('Radio kickoff')
    with open('media.json', 'r') as config_file:
      playlist = json.load(config_file)

    media_index = 0
    errors = 0
    proc = subprocess.Popen(['ffplay', '-autoexit', '-nodisp', '-hide_banner', '-loglevel', 'error', playlist['medias'][media_index]['link']])
    update_oled(playlist['medias'][media_index]['name'])

    # allow extra time to start since ffplay is slow to start
    time.sleep(3)
    while True:
      time.sleep(5)

      result = subprocess.check_output('grep RUNNING /proc/asound/card*/pcm*/sub*/status |wc -l', shell=True, text=True)
      state = int(result.strip())
      print(state)

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
        if media_index >= len(playlist['medias']):
          media_index = 0

        proc = subprocess.Popen(['ffplay', '-autoexit', '-nodisp', '-hide_banner', '-loglevel', 'error', playlist['medias'][media_index]['link']])
        update_oled(playlist['medias'][media_index]['name'])
        # allow extra time to start since ffplay is slow to start
        time.sleep(3)

  except Exception as e:
    traceback.print_exc()
    print(e)
  finally:
    update_oled("")
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
      # lower down volume
      os.system("amixer -q sset PCM '100%-'")
    elif payload['cmd'] == 'increase':
      # louder please !
      os.system("amixer -q sset PCM '100%+'")
    elif payload['cmd'] == 'setvolume':
      # set volume
      try:
        volume = int(payload['volume'])
      except:
        volume = 90
      os.system(f"amixer -q sset PCM '{volume}%'")
    elif payload['cmd'] == 'short_push':
      # move on next media in playlist
      os.system('killall -9 ffplay')
    elif payload['cmd'] == 'simple_push':
      # toggle music
      if process is not None and process.is_alive():
        # stop music
        update_oled("")
        process.terminate()
        process.join()
        process = None
        os.system('killall -9 ffplay')
      else:
        # start music
        process = mp.Process(target=thread_radio)
        process.start()
    elif payload['cmd'] == 'short_push':
        # kill ffplay to move on the next available radio/file
        os.system('killall -9 ffplay')
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

