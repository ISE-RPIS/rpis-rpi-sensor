# MqttClient
## Required
- Python 3.7 recommended
- paho_mqtt

## Using libraries
- time, json, ssl, gc, platform
- paho.mqtt.client

## How to install?
Copy 'rpis_mqtt' directory into 'site-packages' directory, below 'python/lib'.

## How to use?
```
from rpis_mqtt.mqtt import MqttClient
import json

client = MqttClient(endpoint='localhost', port=1883, set_tls=False)

client.connect()
# [MqttClient] mqtt loop start
# [on_connect] Connection OK

client.subscribe('my/topic')
# [on_subscribe] callback mid = 1

payload = json.dumps({'action': 'value'})
client.publish('my/topic', payload=payload)
# [MqttClient] message sending...
# [on_publish] callback mid = 2
# [on_message] mid = 0
# [on_message] topic = my/topic
# [on_message] payload = b'{"action": "value"}'
# [on_message] qos = 0
# [on_message] retain = 0

client.disconnect()
# [on_disconnect] Disconnection OK, rc : 0
```
