import time
# import json
import ssl
import paho.mqtt.client as mqtt
import gc
import platform
import os


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('[on_connect] Connection OK')
    else:
        print('[on_connect] Connection Failed :', str(rc))


def on_disconnect(client, userdata, rc=0):
    if rc == 0:
        print('[on_disconnect] Disconnection OK')
        on_disconnect.retry_count = 0
    else:
        print('[on_disconnect] Disconnection Error, rc :', rc)
        try:
            if on_disconnect.retry_count == -1:
                print('[on_disconnect] for checking variable')
        except Exception as e:
            on_disconnect.retry_count = 0
            print(e)
        if on_disconnect.retry_count < 5:
            on_disconnect.retry_count += 1
            print('[on_disconnect] Checking... (%d/%d)' %
                  (on_disconnect.retry_count, 5))
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


class MqttClient:
    def __init__(self, endpoint, port=1883, set_tls=False):
        self.__endpoint = endpoint
        self.__port = port  # 8883
        self.__ca_certs = os.path.abspath(os.path.dirname(
            __file__) + '/' + './certs/ca_certs.crt')
        self.__certfile = os.path.abspath(os.path.dirname(
            __file__) + '/' + './certs/certificate.pem.crt')
        self.__keyfile = os.path.abspath(os.path.dirname(
            __file__) + '/' + './certs/private.pem.key')
        self.__client = mqtt.Client()
        self.__set_tls = set_tls
        self.reset()

    def debug_print(self, message):
        prefix = '[%s]' % (self.__class__.__name__)
        if type(message) != str:
            print(prefix, 'message type is wrong!')
            return
        if len(message) == 0:
            print(prefix, 'message is empty!')
            return
        print(prefix, message)

    @property
    def endpoint(self):
        return self.__endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        if type(endpoint) != str:
            raise TypeError('"endpoint" is not str!')
        self.__endpoint = endpoint

    @property
    def port(self):
        return self.__port

    @port.setter
    def port(self, port):
        if type(port) != int:
            raise TypeError('"port" is not int!')
        self.__port = port

    @property
    def client(self):
        return self.__client

    @property
    def ca_certs(self):
        return self.__ca_certs

    @ca_certs.setter
    def ca_certs(self, ca_certs):
        if type(ca_certs) != str:
            self.debug_print('"ca_certs" is invalid path')
            raise TypeError('"ca_certs" is invalid path')
        if platform.system().lower() == 'windows' and ca_certs[0] == '~':
            ca_certs = os.environ['USERPROFILE'] + ca_certs[1:]
        self.__ca_certs = os.path.abspath(ca_certs)

    @property
    def certfile(self):
        return self.__certfile

    @certfile.setter
    def certfile(self, certfile):
        if type(certfile) != str:
            self.debug_print('"certfile" is invalid path')
            raise TypeError('"certfile" is invalid path')
        if platform.system().lower() == 'windows' and certfile[0] == '~':
            certfile = os.environ['USERPROFILE'] + certfile[1:]
        self.__certfile = os.path.abspath(certfile)

    @property
    def keyfile(self):
        return self.__keyfile

    @keyfile.setter
    def keyfile(self, keyfile):
        if type(keyfile) != str:
            self.debug_print('"keyfile" is invalid path')
            raise TypeError('"keyfile" is invalid path')
        if platform.system().lower() == 'windows' and keyfile[0] == '~':
            keyfile = os.environ['USERPROFILE'] + keyfile[1:]
        self.__keyfile = os.path.abspath(keyfile)

    @property
    def set_tls(self):
        return self.__set_tls

    @set_tls.setter
    def set_tls(self, set_tls):
        if type(set_tls) != bool:
            self.debug_print('"set_tls" is not bool!')
            raise TypeError('"set_tls" is not bool!')
        self.__set_tls = set_tls

    def reset(self):
        if self.client.is_connected():
            self.disconnect()
        self.client.reinitialise()
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_publish = on_publish
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
        self.client.on_unsubscribe = on_unsubscribe
        if self.set_tls:
            self.client.tls_set(ca_certs=self.ca_certs,
                                certfile=self.certfile,
                                keyfile=self.keyfile,
                                tls_version=ssl.PROTOCOL_TLSv1_2)
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
            if not self.client.is_connected():
                for i in range(3):
                    self.debug_print('connection wait...')
                    time.sleep(5)
                    if self.client.is_connected():
                        break
                if not self.client.is_connected():
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
            _ = self.client.publish(
                topic, payload=payload, qos=qos, retain=retain)
            time.sleep(0.2)
        except NameError:
            raise NameError('"client" is not defined. check client setup.')

    def subscribe(self, topic, qos=0, options=None, properties=None):
        try:
            if not self.client.is_connected():
                for i in range(3):
                    self.debug_print('connection wait...')
                    time.sleep(5)
                    if self.client.is_connected():
                        break
                if not self.client.is_connected():
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
            _ = self.client.subscribe(
                topic, qos=qos, options=options, properties=properties)
            time.sleep(0.2)
        except NameError:
            raise NameError('"client" is not defined. check client setup.')
