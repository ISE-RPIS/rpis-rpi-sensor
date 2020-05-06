import RPi.GPIO as GPIO

import time

import picamera

from picamera import PiCamera

import datetime

from time import sleep

 

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

trig = 2

echo = 3

GPIO.setup(trig, GPIO.OUT)

GPIO.setup(echo, GPIO.IN)

temp = 0

 

try:

    while True:

 

        GPIO.output(trig, False)

        time.sleep(0.5)

 

        GPIO.output(trig, True)

        time.sleep(0.0001)

        GPIO.output(trig, False)

 

        while GPIO.input(echo) == 0:

            pulse_start = time.time()

 

        while GPIO.input(echo) == 1:

            pulse_end = time.time()

 

        pulse_duration = pulse_end - pulse_start

        distance = pulse_duration * 17000

        distance = round(distance, 2)

 

        print(' distance : ', distance, 'cm')

        now = datetime.datetime.now()

        now_str=now.strftime('%Y-%m-%d,%p%l:%M:%S.h264')

 

        if(temp==0 and distance < 10):

            temp = 1

            camera = PiCamera()
            
            camera.resolution = (2592, 1944)
            
            camera.framerate = 15
    
            camera.start_preview()
            
            sleep(5)
            
            camera.capture('/home/pi/capture.jpg')

            camera.stop_preview()


            print('Sensoring')
            
            sleep(5)

        elif(temp==1 and distance >= 10):

            temp = 0

            print('OK')

            camera.close()

 

except KeyboardInterrupt:

    GPIO.cleanup()
