
#
# abandon
# python/vlc and vlc are way too slow. Getting a lot of those and sound is rubbish
# [007d92a8] alsa audio output error: cannot estimate delay: Relais brisé (pipe)
#

import configparser
import vlc
import time
import subprocess
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
    player = vlc.MediaPlayer(sound_list[url_index])
    player.play()

    while True:
      print(player.get_media().get_mrl())
      time.sleep(5)

      result = subprocess.check_output('grep RUNNING /proc/asound/card*/pcm*/sub*/status |wc -l', shell=True, text=True)
      state = int(result.strip())

      print(f"errors: {errors} player.get_state: {player.get_state()} state: {state}")

      # make sure sound is coming out of player
      if player.get_state() != vlc.State.Playing or state == 0:
        # player stopped or no music/radio is beeing played (netwok issue or remote server issue)!
        errors = errors + 1
      else:
        errors = 0

      if errors > 3:
        # too many errors, swapping on next media
        player.stop()
        errors = 0
        url_index = url_index + 1
        if url_index > len(sound_list):
          url_index = 0
          if sound_list == radio_fallback:
            sound_list = radio_fallback
          else:
            sound_list = radio_fallback

        player = vlc.MediaPlayer(sound_list[url_index])
        print(sound_list[url_index])
        player.play()

  except Exception as e:
    traceback.print_exc()
    print(e)

