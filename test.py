from packages.rpis_mqtt.mqtt import MqttClient
from packages.rpis_camera.camera import Camera
from packages.rpis_lpr.LPR import LPR
import numpy as np
import json, ssl, os, platform, gc
import RPi.GPIO as GPIO
from time import sleep, time

ULTRASOUNDS_TRIG = -1
ULTRASOUNDS_ECHO = -1
ULTRASOUNDS_DISTANCE = 7
QUIT_BUTTON_PIN = -1
PARKING_ID = 000000
MODE = 0
LED1_PIN = -1
LED2_PIN = -1
LED3_PIN = -1
LED4_PIN = -1

print('[RPIS] Activate RPIS main process...')

AWS_IOT_ENDPOINT = 'a3d767kqnxh4m3-ats.iot.ap-northeast-2.amazonaws.com'
AWS_IOT_PORT = 8883

program_running = True
def buttonOnClick(channel):
    global program_running
    program_running = False
    print('[RPIS] Quit button pressed!')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ULTRASOUNDS_TRIG, GPIO.OUT)
GPIO.setup(ULTRASOUNDS_ECHO, GPIO.IN)
GPIO.setup(QUIT_BUTTON_PIN, GPIO.IN, GPIO.PUD_UP)
GPIO.setup(LED1_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)
GPIO.setup(LED3_PIN, GPIO.OUT)
GPIO.setup(LED4_PIN, GPIO.OUT)
GPIO.add_event_detect(QUIT_BUTTON_PIN, GPIO.FALLING, buttonOnClick)

obj_detect_start = -1
obj_detected = False

try:
    GPIO.output(LED1_PIN, True)
    while program_running:
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

        if distance <= ULTRASOUNDS_DISTANCE:
            if obj_detected:
                continue
            if obj_detect_start == -1:
                obj_detect_start = time()
            obj_detect_end = time()
            # checking 2 sec
            if obj_detect_end - obj_detect_start >= 2:
                print('[RPIS] 1. Detected!!!')
                obj_detected = True

                # Capture
                cam = Camera()
                cam.sensor_mode = 6
                cam.rotation = 180
                image = cam.capture_to_opencv()
                GPIO.output(LED2_PIN, True)
                print('[RPIS] 2. Capturing image is successfully!')

                # Get license text
                plate_char = LPR().get_license_plate_char(image)
                GPIO.output(LED3_PIN, True)
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
                # client = MqttClient(endpoint=AWS_IOT_ENDPOINT,
                #                     port=AWS_IOT_PORT, set_tls=True)
                # client.connect()
                # if MODE == 0:
                #     client.publish('iot/rpis/coming', json.dumps(data))
                # else:
                #     client.publish('iot/rpis/outgoing', json.dumps(data))
                GPIO.output(LED4_PIN, True)
                print('[RPIS] 4. Sending data is successfully!')
                print(json.dumps(data, indent=4))
                gc.collect()
        else:
            obj_detected = False
            obj_detect_start = -1
            GPIO.output(LED2_PIN, False)
            GPIO.output(LED3_PIN, False)
            GPIO.output(LED4_PIN, False)
except Exception as e:
    print('[RPIS] Error: Occured exception!!!')
    print(e)
finally:
    GPIO.cleanup()
    print('[RPIS] GPIO cleanup successfully!')

print('[RPIS] Program exit successfully!')
