from picamera Import PiCamera
from time import sleep
import RPi.GPIO as GPIO
'''
DETECT_TIME = 3
ULTRASOUNDS_TRIG = 13
ULTRASOUNDS_ECHO = 19

def detectAndCapture(path, imgName):
    GPIO.setup(ULTRASOUNDS_TRIG, GPIO.OUT)
    GPIO.setup(ULTRASOUNDS_ECHO, GPIO.IN)
    
    with PiCamera() as camera:
        

    GPIO.cleanup()
    return 0
'''
class VehicleDetect:
    def __init__(self, trig, echo, duration=34000/2, detect_time=3):
        if type(trig) != int:
            raise TypeError('"trig" is must be integer!')
        if type(echo) != int:
            raise TypeError('"echo" is must be integer!')
        if not(type(duration) == int or type(duration) == float):
            raise TypeError('"duration" is must be numeric!')
        if type(detect_time) != int:
            raise TypeError('"detect_time" is must be integer!')
        
        self.gpio_trig = int(trig)
        self.gpio_echo = int(echo)
        self.duration = duration
        self.detect_time = detect_time

    def detectAndCapture(self, path, imgName):
        if type(path) != str or type(imgName) != str:
            raise TypeError('"path" and "imgName" are must be string!')
        
