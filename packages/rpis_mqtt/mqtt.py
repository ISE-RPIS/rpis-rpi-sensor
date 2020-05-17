import time, json, ssl
import paho.mqtt.client as mqtt
import gc, platform

def on_connect(client, userdata, flags, rc):
    if rc == 0:
            print('[on_connect] Connection OK')
    else:
            print('[on_connect] Connection Failed :', str(rc))

@static_vars(retry_count=0)
def on_disconnect(client, userdata, rc=0):
    if rc == 0:
        print('[on_disconnect] Disconnection OK')
        on_disconnect.retry_count = 0
    else:
        print('[on_disconnect] Disconnection Error, rc :', rc)
        if on_disconnect.retry_count < 5:
            on_disconnect.retry_count += 1
        else:
            print('[on_disconnect] Disconnection Error, client loop stop')
            on_disconnect.retry_count = 0
            client.loop_stop()

def on_publish(client, userdata, mid):
    print('[on_publish] callback mid =', mid)

def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    print('[on_subscribe] callback mid =', mid)

def on_unsubscribe(client, userdata, mid):
    print('[on_unsubscribe] callback mid =', mid)

def on_message(client, userdata, message):
    print('[on_message] mid =', message.mid)
    print('[on_message] topic =', message.topic)
    print('[on_message] payload =', message.payload)
    print('[on_message] qos =', message.qos)
    print('[on_message] retain =', message.retain)

def debug_print(module, message):
    if type(message) != str:
        print('[debug_print] message type is wrong!')
        return
    print

def convert_path_for_windows(path):
    path_obj = path.split('/')
    winpath = ''
    if len(path_obj[0]) == 0:
        path_obj = path_obj[1:]
        winpath = path_obj[0] + ':\\'
        path_obj = path_obj[1:]
    winpath += '\\'.join(path_obj)
    return winpath

class MqttClient:
    def __init__(self, endpoint, port=1883, set_tls=False):
        self.endpoint = endpoint
        self.port = port #8883
        self.ca_certs = './certs/ca_certs.crt'
        self.certfile = './certs/certificate.pem.crt'
        self.keyfile = './certs/private.pem.key'
        if platform.system().lower() == 'windows':
            self.ca_certs = convert_path_for_windows(self.ca_certs)
            self.certfile = convert_path_for_windows(self.certfile)
            self.keyfile = convert_path_for_windows(self.keyfile)
        self.client = mqtt.Client()
        self.reset()

    def debug_print(self, message):
        prefix = '[%s]'%(MqttClient.__name__)
        if type(message) != str:
            print(prefix, 'message type is wrong!')
            return
        if len(message) == 0:
            print(prefix, 'message is empty!')
            return
        print(prefix, message)

    def reset(self, set_tls=False, ca_certs=None, certfile=None, keyfile=None, tls_version=ssl.PROTOCOL_TLSv1_2):
        if self.client.is_connected():
            self.disconnect()
        self.client.reinitialise()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
        self.client.on_unsubscribe = on_unsubscribe
        if set_tls:
            if ca_certs != None:
                if type(ca_certs) != str:
                    raise TypeError('"ca_certs" type must be str!')
                self.ca_certs = ca_certs
            if certfile != None:
                if type(certfile) != str:
                    raise TypeError('"certfile" type must be str!')
                self.certfile = certfile
            if keyfile != None:
                if type(keyfile) != str:
                    raise TypeError('"keyfile" type must be str!')
                self.keyfile = keyfile
            self.client.tls_set(ca_certs = self.ca_certs,
                                certfile = self.certfile,
                                keyfile = self.keyfile,
                                tls_version = tls_version)
        gc.collect()

    def connect(self):
        try:
            if type(self.endpoint) != str:
                raise TypeError('"endpoint" type must be str!')
            elif len(self.endpoint) == 0:
                raise ValueError('"endpoint" is empty!')
            if type(self.port) != int:
                raise TypeError('"port" type must be int!')
            _ = self.client.connect(self.endpoint, port=self.port)
            self.debug_print('mqtt loop start')
            _ = self.client.loop_start()
        except NameError:
            raise NameError('"client" is not defined. check client setup.')

    def disconnect(self):
        try:
            _ = self.client.disconnect()
            time.sleep(0.2)
            _ = self.client.loop_stop()
        except NameError:
            raise NameError('"client" is not defined. check client setup.')

    def publish(self, topic, payload, qos=0, retain=False):
        try:
            if self.client.is_connected() == False:
                for i in range(3):
                    self.debug_print('connection wait...')
                    time.sleep(5)
                    if self.client.is_connected():
                        break
                if self.client.is_connected() == False:
                    self.debug_print('connection failed')
                    self.disconnect()
                    return
            if type(topic) != str:
                raise TypeError('"topic" type must be str!')
            elif len(topic) == 0:
                raise ValueError('"topic" is empty!')
            if type(payload) != str:
                raise TypeError('"payload" type must be str!')
            elif len(payload) == 0:
                raise ValueError('"payload" is empty!')
            if type(qos) != int:
                raise TypeError('"qos" type must be int!')
            elif qos < 0 or qos > 2:
                raise ValueError('"qos" is wrong! (range: 0~2)')
            if type(retain) != bool:
                raise TypeError('"retain" type must be bool!')
            self.debug_print('message sending...')
            time.sleep(0.2)
            _ = self.client.publish(topic, payload=payload, qos=qos, retain=retain)
            time.sleep(0.2)
        except NameError:
            raise NameError('"client" is not defined. check client setup.')

    def subscribe(self, topic, qos=0, options=None, properties=None):
        try:
            if self.client.is_connected() == False:
                for i in range(3):
                    self.debug_print('connection wait...')
                    time.sleep(5)
                    if self.client.is_connected():
                        break
                if self.client.is_connected() == False:
                    self.debug_print('connection failed')
                    self.disconnect()
                    return
            if type(topic) != str:
                raise TypeError('"topic" type must be str!')
            elif len(topic) == 0:
                raise ValueError('"topic" is empty!')
            if type(qos) != int:
                raise TypeError('"qos" type must be int!')
            elif qos < 0 or qos > 2:
                raise ValueError('"qos" is wrong! (range: 0~2)')
            # TODO: type & value check of 'options', 'properties'
            time.sleep(0.2)
            _ = self.client.subscribe(topic, qos=qos, options=options, properties=properties)
            time.sleep(0.2)
        except NameError:
            raise NameError('"client" is not defined. check client setup.')

