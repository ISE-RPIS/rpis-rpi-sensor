import time, json, ssl
import paho.mqtt.client as mqtt

AWS_IOT_ENDPOINT = 'a3d767kqnxh4m3-ats.iot.ap-northeast-2.amazonaws.com'

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('connection OK')

def on_disconnect(client, userdata, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print('in on_pub callback mid =', mid)

client = mqtt.Client()
client.on_connect = on_connect
client.on_disconnect = on_disconnect
client.on_publish = on_publish

ca_certs = './certs/ca_certs.crt'
certfile = './certs/certificate.pem.crt'
keyfile = './certs/private.pem.key'

client.tls_set(ca_certs=ca_certs,
               certfile=certfile,
               keyfile=keyfile,
               tls_version=ssl.PROTOCOL_TLSv1_2)
client.connect(AWS_IOT_ENDPOINT, port=8883)
client.loop_start()

# do something
'''
#topic = 'rpis/test'
#payload = json.dumps({'action': 'test'})
#qos = 1
client.publish(topic=topic, payload=payload, qos=qos)
'''

client.loop_stop()

