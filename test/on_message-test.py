import paho.mqtt.client as mqtt
from datetime import datetime as dt
import json

def on_connect(client, userdata, flags, reason_code, properties=None):
  client.subscribe(topic="alarmclock_sound")
  client.subscribe(topic="alarmclock_menu")

def on_message(client, userdata, message, properties=None):
  payload = json.loads(message.payload)
  print(f"Topic: {message.topic}, payload: {payload}")
  
def on_subscribe(client, userdata, mid, qos, properties=None):
  print(f"{dt.now()} Subscribed with QoS {qos}")


client = mqtt.Client(client_id="alarmclock", protocol=mqtt.MQTTv311, clean_session=True)
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host="127.0.0.1", port=1883, keepalive=60)
client.loop_forever()
