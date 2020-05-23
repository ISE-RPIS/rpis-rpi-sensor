from rpis_mqtt.mqtt import MqttClient
from rpis_camera.camera import Camera
from rpis_lpr import LPR
import numpy as np
#import cv2
import json, ssl, os, platform, gc
import RPi.GPIO as GPIO
from time import sleep, time

AWS_IOT_ENDPOINT = 'a3d767kqnxh4m3-ats.iot.ap-northeast-2.amazonaws.com'
AWS_IOT_PORT = 8883

ULTRASOUNDS_TRIG = 5
ULTRASOUNDS_ECHO = 6
QUIT_BUTTON_PIN = 12

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(ULTRASOUNDS_TRIG, GPIO.OUT)
GPIO.setup(ULTRASOUNDS_TRIG, GPIO.IN)

try:
    while True:
        # TODO: escape 방안 고민, 버튼을 달까?
        
        GPIO.output(ULTRASOUNDS_TRIG, False)
        sleep(0.5)
        GPIO.output(ULTRASOUNDS_TRIG, True)
        sleep(0.00001)
        GPIO.output(ULTRASOUNDS_TRIG, False)

        while GPIO.input(UTLRASOUNDS_ECHO) == 0:
            pulse_start = time()
        while GPIO.input(ULTRASOUNDS_ECHO) == 1:
            pulse_end = time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 34000 / 2
        distance = round(distance, 2)

        print('Distance :', distance, 'cm')

        if distance <= 25:
            # checking per 50ms
            #sleep(0.05)
            if obj_detect_start == -1:
                obj_detect_start = time()
            obj_detect_end = time()
            # checking 2 sec
            if obj_detect_end - obj_detect_start >= 2:
                # TODO: Capture & Report to DB
        else:
            obj_detect_start = -1
finally:
    GPIO.cleanup()
