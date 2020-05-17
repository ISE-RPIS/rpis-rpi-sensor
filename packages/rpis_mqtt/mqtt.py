import time, json, ssl
import paho.mqtt.client as mqtt
import gc

def on_connect(client, userdata, flags, rc):
    if rc == 0:
            print('[on_connect] Connection OK')
    else:
            print('[on_connect] Connection Failed :', str(rc))
            
def on_disconnect(client, userdata, rc=0):
    print('[on_disconnect] Disconnection OK, rc :', rc)
        
def on_publish(client, userdata, mid):
    print('[on_publish] callback mid =', mid)


class AWS_MessagePublisher:
    def __init__(self):
        self.endpoint = ''
        self.port = 1883 #8883
        self.ca_certs = './certs/ca_certs.crt'
        self.certfile = './certs/certificate.pem.crt'
        self.keyfile = './certs/private.pem.key'

    def setup(self, set_tls=False):
        self.client = mqtt.Client()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
		if set_tls:
            self.client.tls_set(ca_certs = self.ca_certs,
                                certfile = self.certfile,
                                keyfile = self.keyfile,
                                tls_version = ssl.PROTOCOL_TLSv1_2)
        gc.collect()

    def publish(self, topic, payload, qos=0, retain=False):
        try:
            if self.client == None:
                print('client is not defined. check client setup.')
                return
        except NameError:
            print('client is not defined. check client setup.')
            return
        if type(topic) != str or len(topic) == 0:
            print('topic is wrong :', topic)
            return
        if type(payload) != str or len(payload) == 0:
            print('payload is wrong :', payload)
            return
        print('[%s]'%(AWS_MessagePublisher.__name__), 'mqtt loop start')
        _ = self.client.connect(self.endpoint, port=self.port)
        _ = self.client.loop_start()
        print('[%s]'%(AWS_MessagePublisher.__name__), 'message sending...')
        time.sleep(0.5)
        _ = self.client.publish(topic, payload=payload, qos=qos, retain=retain)
        time.sleep(0.5)
        _ = self.client.disconnect()
        _ = self.client.loop_stop()
        print('[%s]'%(AWS_MessagePublisher.__name__), 'mqtt loop stop')

