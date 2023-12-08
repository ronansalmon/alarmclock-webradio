import configparser
import time
import subprocess, os
import traceback

if __name__ == '__main__':
  try:
    config = configparser.ConfigParser()
    config.read('../config.ini')
    radio_url = config['default']['radio_url'].split("\n")
    radio_fallback = config['default']['radio_fallback'].split("\n")

    url_index = 0
    errors = 0
    sound_list = radio_url
    proc = subprocess.Popen(['ffplay', '-nodisp', '-hide_banner', '-loglevel', 'error', sound_list[url_index]])
    # allow extra time to start since ffplay is slow to start
    time.sleep(3)
    while True:
      print(sound_list[url_index])
      time.sleep(5)

      result = subprocess.check_output('grep RUNNING /proc/asound/card*/pcm*/sub*/status |wc -l', shell=True, text=True)
      state = int(result.strip())

      print(f"errors: {errors} state: {state}")
      # make sure sound is coming out of player
      if state == 0:
        # player stopped or no music/radio is beeing played (netwok issue or remote server issue)!
        errors = errors + 1
      else:
        errors = 0
      
      # proc is dead
      if proc.poll() is not None:
        errors = 99

      if errors > 3:
        # too many errors, swapping on next media
        proc.terminate()
        errors = 0
        url_index = url_index + 1
        if url_index >= len(sound_list):
          url_index = 0
          if sound_list == radio_url:
            sound_list = radio_fallback
          else:
            sound_list = radio_url

        proc = subprocess.Popen(['ffplay', '-nodisp', '-hide_banner', '-loglevel', 'error', sound_list[url_index]])
        # allow extra time to start since ffplay is slow to start
        time.sleep(3)

  except Exception as e:
    os.system('killall -9 ffplay')
    traceback.print_exc()
    print(e)

