import configparser
import traceback
import paho.mqtt.client as mqtt
import json
import time
import board
import digitalio
import adafruit_ssd1306
from ast import literal_eval
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

client_id = "alarmclock_oled"
topic = "alarmclock_oled"
auto_refresh = 1

# Setting some variables for our reset pin etc.
RESET_PIN = digitalio.DigitalInOut(board.D4)
i2c = board.I2C()  # uses board.SCL and board.SDA
oled = None
image = None
fonttime = ImageFont.truetype("Courier_New_Bold", 42)
fontother = ImageFont.truetype("DejaVuSerif",10)
alarm_text = ""
media_text = ""

def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic=topic)

def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"Subscribed with QoS {qos}")

def on_message(client, userdata, message, properties=None):
  global media_text, alarm_text, auto_refresh
  try:
    payload = json.loads(message.payload)
    if payload['cmd'] == 'media_text':
      media_text = payload['text']
    elif payload['cmd'] == 'alarm_text':
      alarm_text = payload['text']
    elif payload['cmd'] == 'alarm_setup':
      auto_refresh = float(payload['text'])
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
    auto_refresh = float(config['oled']['auto_refresh'])
    oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=literal_eval(config['oled']['address']), reset=RESET_PIN)
    oled.contrast(int(config['oled']['contrast']))
    oled.fill(0)
    oled.show()
    
    if alarm_enable:
      alarm_text = time.strftime("%H:%M", time.gmtime(int(config['alarm']['alarm_time'])))

    image = Image.new('1', (oled.width, oled.height))
    draw = ImageDraw.Draw(image)
    now = datetime.now()
    draw.text((2, 0), now.strftime("%H:%M"),  font=fonttime, fill=255)
    draw.text((70, 53), now.strftime("%d/%m/%Y"),  font=fontother, fill=255) 
    draw.text((0, 40), media_text,  font=fontother, fill=255) 
    draw.text((00, 53), alarm_text,  font=fontother, fill=255) 
    oled.image(image)
    oled.show()

    client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_subscribe = on_subscribe
    client.connect(host="127.0.0.1", port=1883, keepalive=60)
    
    client.loop_start()
    loop = 0

    while True:
      image = Image.new('1', (oled.width, oled.height))
      draw = ImageDraw.Draw(image)
      now = datetime.now()
      if loop % 2 != 0:
        draw.text((2, 0), now.strftime("%H:%M"),  font=fonttime, fill=255)
      else:
        draw.text((2, 0), now.strftime("%H %M"),  font=fonttime, fill=255)
      loop += 1
      
      draw.text((70, 53), now.strftime("%d/%m/%Y"),  font=fontother, fill=255) 
      draw.text((0, 40), media_text,  font=fontother, fill=255) 
      draw.text((00, 53), alarm_text,  font=fontother, fill=255) 
      oled.image(image)
      oled.show()
      time.sleep(auto_refresh)
    
  except Exception as e:
    traceback.print_exc()
    print(e)

