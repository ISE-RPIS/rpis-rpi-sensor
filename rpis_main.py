from rpis_mqtt.mqtt import MqttClient
from rpis_camera.camera import Camera
from rpis_lpr import LPR
import numpy as np
import json, ssl, os, platform, gc
import RPi.GPIO as GPIO
from time import sleep, time

AWS_IOT_ENDPOINT = 'a3d767kqnxh4m3-ats.iot.ap-northeast-2.amazonaws.com'
AWS_IOT_PORT = 8883

ULTRASOUNDS_TRIG = 5
ULTRASOUNDS_ECHO = 6
QUIT_BUTTON_PIN = 24

while True:
    PARKING_ID = input('[RPIS] Set "parking_id": ')
    if input('[RPIS] "{0}" Is correct? (y/n) : '.format(PARKING_ID)).lower() == 'y':
        break

while True:
    MODE = input('[RPIS] Set mode (0: coming, 1: outgoing): ')
    try:
        MODE = int(MODE)
    except:
        print('[RPIS] Occured exception! : Failed type casting "MODE"')
        continue
    if MODE < 0 or MODE > 1:
        print('[RPIS] Error: Invalid value!')
        continue
    if input('[RPIS] "{0}" is correct? (y/n) : '.format(MODE)).lower() == 'y':
        break

print('[RPIS] Activate RPIS main process...')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ULTRASOUNDS_TRIG, GPIO.OUT)
GPIO.setup(ULTRASOUNDS_ECHO, GPIO.IN)
GPIO.setup(QUIT_BUTTON_PIN, GPIO.IN, GPIO.PUD_UP)

try:
    while True:
        if GPIO.input(QUIT_BUTTON_PIN) == False:
            break

        # Loop time: 500ms + @
        GPIO.output(ULTRASOUNDS_TRIG, False)
        sleep(0.5)
        GPIO.output(ULTRASOUNDS_TRIG, True)
        sleep(0.00001)
        GPIO.output(ULTRASOUNDS_TRIG, False)

        while GPIO.input(ULTRASOUNDS_ECHO) == 0:
            pulse_start = time()
        while GPIO.input(ULTRASOUNDS_ECHO) == 1:
            pulse_end = time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 34000 / 2
        distance = round(distance, 2)

        print('[RPIS] Distance :', distance, 'cm')

        if distance <= 25:
            if obj_detect_start == -1:
                obj_detect_start = time()
            obj_detect_end = time()
            # checking 2 sec
            if obj_detect_end - obj_detect_start >= 2:
                print('[RPIS] 1. Detected!!!')
                # Capture
                cam = Camera()
                cam.sensor_mode = 6
                cam.rotation = 180
                image = cam.capture_to_opencv()
                print('[RPIS] 2. Capturing image is successfully!')
                # Get license text
                plate_char = LPR().get_license_plate_char(image)
                print('[RPIS] 3. Getting license text is successfully!')
                print('[RPIS] license : {0}'.format(plate_char))
                # Send to AWS IoT using MQTT
                data = {}
                data['license'] = plate_char
                data['parking_id'] = PARKING_ID
                if MODE == 0:
                    data['coming_time'] = str(time())
                else:
                    data['outgoing_time'] = str(time())
                client = MqttClient(endpoint=AWS_IOT_ENDPOINT, port=AWS_IOT_PORT, set_tls=True)
                client.connect()
                if MODE == 0:
                    client.publish('iot/rpis/coming', json.dumps(data))
                else:
                    client.publish('iot/rpis/outgoing', json.dumps(data))
                print('[RPIS] 4. Sending data is successfully!')
                print(json.dumps(data, indent=4))
        else:
            obj_detect_start = -1
except:
    print('[RPIS] Error: Occured exception!!!')
finally:
    GPIO.cleanup()
    print('[RPIS] GPIO cleanup successfully!')

print('[RPIS] Program exit successfully!')
