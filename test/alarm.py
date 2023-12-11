import configparser
import datetime
import json
import traceback
from time import strftime
from time import gmtime


if __name__ == '__main__':
  try:
      
    config = configparser.ConfigParser()
    config.read('../config.ini.default')
    alarm = int(config['alarm']['alarm_time'])
    now = datetime.datetime.now()
    sleep = 0
    seconds_so_far = now.hour * 3600 + now.minute * 60  + now.second
    
    print(f"Alarm set to '{alarm}'")
    print(str(datetime.timedelta(seconds=alarm)))

    print(strftime("%H:%M", gmtime(alarm)))

    print(f"now: {seconds_so_far}")
    if seconds_so_far > alarm:
      sleep = alarm + (24 * 3600 - seconds_so_far)
    else:
      sleep = alarm - seconds_so_far

    # sanity check
    if sleep < 1:
      sleep = 1
      
    print(f"Sleep for {sleep} seconds")
    

  except Exception as e:
    traceback.print_exc()
    print(e)
