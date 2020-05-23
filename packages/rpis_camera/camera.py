from picamera import PiCamera
from time import sleep
import numpy as np
import cv2
import platform, os

'''
def convert_path_for_windows(path):
    path_obj = path.split('/')
    if len(path_obj[-1]) != 0:
        path_obj.append('')
    winpath = ''
    if len(path_obj[0]) == 0:
        path_obj = path_obj[1:]
        winpath = path_obj[0] + ':\\'
        path_obj = path_obj[1:]
    if path_obj[0] == '~':
        path_obj = path_obj[1:]
        path_obj.insert(0, os.environ['USERPROFILE'])
    winpath += '\\'.join(path_obj)
    return winpath
'''

class Camera:
    def __init__(self):
        self.__resolution = (1920,1080)
        self.__framerate = 30
        self.__brightness = 50
        self.__contrast = 0
        self.__rotation = 0
        self.__hflip = False
        self.__vflip = False
        self.__sensor_mode = 0

    def debug_print(self, message):
        prefix = '[%s]'%(self.__class__.__name__)
        if type(message) != str:
            print(prefix, 'message type is wrong!')
            return
        if len(message) == 0:
            print(prefix, 'message is empty!')
            return
        print(prefix, message)

    @property
    def resolution(self):
        return self.__resolution
    @resolution.setter
    def resolution(self, resolution):
        if type(resolution) != tuple:
            self.debug_print('"resolution" is not tuple!')
            raise TypeError('"resolution" is not tuple!')
        if len(resolution) != 2:
            self.debug_print('"resolution" must have 2 items : {0}'.format(resolution))
            raise ValueError('"resolution" must have 2 items : {0}'.format(resolution))
        for t in resolution:
            if type(t) != int:
                self.debug_print('"resolution" value is not int! : {0}'.format(t))
                raise ValueError('"resolution" value is not int! : {0}'.format(t))
        self.__resolution = resolution

    @property
    def framerate(self):
        return self.__framerate
    @framerate.setter
    def framerate(self, framerate):
        if type(framerate) != int:
            self.debug_print('"framerate" is not int!')
            raise TypeError('"framerate" is not int!')
        if framerate < 10 or framerate > 90:
            self.debug_print('"framerate" is invalid (10~90) : {0}'.format(framerate))
            raise ValueError('"framerate" is invalid (10~90) : {0}'.format(framerate))
        self.__framerate = framerate

    @property
    def brightness(self):
        return self.__brightness
    @brightness.setter
    def brightness(self, brightness):
        if type(brightness) != int:
            self.debug_print('"brightness" is not int!')
            raise TypeError('"brightness" is not int!')
        if brightness < 0 or brightness > 100:
            self.debug_print('"brightness" is invalid (0~100)')
            raise ValueError('"brightness" is invalid (0~100)')
        self.__brightness = brightness

    @property
    def contrast(self):
        return self.__contrast
    @contrast.setter
    def contrast(self, contrast):
        if type(contrast) != int:
            self.debug_print('"contrast" is not int!')
            raise TypeError('"contrast" is not int!')
        if contrast < 0 or contrast > 100:
            self.debug_print('"contrast" is invalid (0~100)')
            raise ValueError('"contrast" is invalid (0~100)')
        self.__contrast = contrast

    @property
    def rotation(self):
        return self.__rotation
    @rotation.setter
    def rotation(self, rotation):
        if type(rotation) != int:
            self.debug_print('"rotation" is not int!')
            raise TypeError('"rotation" is not int!')
        valid = [0, 90, 180, 270]
        if not rotation in valid:
            self.debug_print('"rotation" is invalid {0} : {1}'.format(valid, rotation))
            raise ValueError('"rotation" is invalid {0} : {1}'.format(valid, rotation))
        self.__rotation = rotation

    @property
    def hflip(self):
        return self.__hflip
    @hflip.setter
    def hflip(self, hflip):
        if type(hflip) != bool:
            self.debug_print('"hflip" is not bool!')
            raise TypeError('"hflip" is not bool!')
        self.__hflip = hflip

    @property
    def vflip(self):
        return self.__vflip
    @vflip.setter
    def vflip(self, vflip):
        if type(vflip) != bool:
            self.debug_print('"vflip" is not bool!')
            raise TypeError('"vfilp" is not bool!')
        self.__vflip = vflip

    @property
    def sensor_mode(self):
        return self.__sensor_mode
    @sensor_mode.setter
    def sensor_mode(self, sensor_mode):
        if type(sensor_mode) != int:
            self.debug_print('"sensor_mode" is not int!')
            raise TypeError('"sensor_mode" is not int!')
        if sensor_mode < 0 or sensor_mode > 7:
            self.debug_print('"sensor_mode" is invalid (0~7) : {0}'.format(sensor_mode))
            raise ValueError('"sensor_mode" is invalid (0~7) : {0}'.format(sensor_mode))
        self.__sensor_mode = sensor_mode


    def capture(self, path='~', img_name='capture.jpg'):
        if type(path) != str:
            self.debug_print('"path" must be string!')
            raise TypeError('"path" must be string!')
        if len(path) == 0:
            self.debug_print('"path" is empty!')
            raise ValueError('"path" is empty!')
        for w in path:
            if w.lower() < 'a' or w.lower() > 'z':
                if '!@#$%^&*)(][}{><-=+_`|?.,;:\'\"'.count(w):
                    self.debug_print('"path" is invalid')
                    raise ValueError('"path" is invalid')
        if path[-1] != '/':
            path += '/'
        #if platform.system().lower() == 'windows':
        #    path = convert_path_for_windows(path)

        if type(img_name) != str:
            self.debug_print('"img_name" must be string!')
            raise TypeError('"img_name" must be string!')
        if len(img_name) == 0:
            self.debug_print('"img_name" is empty!')
            raise ValueError('"img_name" is empty!')
        for w in img_name:
            if w.lower() < 'a' or w.lower() > 'z':
                if '!@#$%^&*)(][}{/><-=+_`~|\\?,;:\'\"'.count(w):
                    self.debug_print('"img_name" is invalid')
                    raise ValueError('"img_name" is invalid')
        if len(img_name.split('.')) < 2:
            self.debug_print('"img_name" not included formatter')
            raise ValueError('"img_name" not included formatter')
        if not img_name.split('.')[-1] in ['jpg', 'png', 'gif']:
            self.debug_print('"{0}" format is not supported'.format(img_name.split('.')[-1]))
            raise ValueError('"{0}" format is not supported'.format(img_name.split('.')[-1]))

        #im_name, im_format = '.'.join(img_name.split('.')[:-1]), img_name.split('.')[-1]
        #im_format = ('jpeg' if im_format == 'jpg' else im_format)
        #if platform.system().lower() == 'windows' and path[0] == '~':
        #    path = os.environ['USERPROFILE'] + ('' if len(path) == 1 else path[1:])

        #if platform.system().lower() == 'windows' and path[0] == '~':
        #    path = os.environ['USERPROFILE'] + path[1:]
        if path[0] == '~':
            if platform.system().lower() == 'windows':
                path = os.environ['USERPROFILE'] + path[1:]
            else:
                path = os.environ['HOME'] + path[1:]
        save_path = os.path.abspath(path + '/' + img_name)

        with PiCamera() as camera:
            # rotation set
            # 0, 90, 180, 270
            #camera.rotation = 180

            # saturation(채도) set
            # -100 ~ 100, default 0
            #camera.saturation = -100

            # maximum resolution(해상도) is (2592,1944) for photo, (1920,1080) for video
            # minimum resolution is (64,64)
            # framerate must be 15 if use maximum resolution
            # default, resolution of monitor
            #camera.resolution = (2592, 1944)

            # frame rate
            #camera.framerate = 30

            # brightness(밝기) range : 0 ~ 100, default 50
            #camera.brightness = 50

            # contrast(대비) range : 0 ~ 100, default 0
            #camera.contrast = 50

            # Auto White Balance(화이트밸런스), default 'auto'
            # off, auto, sunlight, cloudy, shade, tungsten, fluorescent, incandescent, flash, horizon
            #camera.awb_mode = 'auto'

            # Exposure(노출), default 'auto'
            # off, auto, night, nightpreview, backlight, spotlight
            # sports, snow, beach, verylong, fixedfps, antishake, fireworks
            #camera.exposure_mode = 'auto'

            # ISO value
            # high : sensitive to light, high speed shutter
            # low : not sensitive to light, low speed shutter
            #print(camera.ISO)

            # iso setting
            # 100, 200, 320, 400, 500, 640, 800
            # v1 module : 100 is 1.0, 800 is 8.0
            # v2 module : 100 is 1.84, 800 is 14.72
            #camera.iso = 320

            # exposure speed(셔터 속도), default 0 (auto)
            # equal shutter_speed
            # if you set shutter_speed to 0, you can get actual shutter speed from this attribute
            # read-only property
            #print(camera.exposure_speed)

            # flip
            #camera.hflip = True
            #camera.vflip = True

            # shutter_speed
            # microseconds
            # default 0 (auto)

            # sensor_mode (1~7), default 0
            # if you set this, don't set 'resolution' and 'framerate'
            '''
            v2 module
            0 : not use(auto resolution and framerate), default
            1 : 1920x1080, 16:9, fps<=30, partial
            4 : 1640x1232, 4:3, fps<=40, full
            5 : 1640x922, 16:9, fps<=40, full
            6 : 1280x720, 16:9, 40<fps<=90, partial
            7 : 640x480, 4:3, 40<fps<=90, partial
            '''
            #camera.sensor_mode = 6

            if self.sensor_mode != 0:
                camera.sensor_mode = self.sensor_mode
            else:
                camera.resolution = self.resolution
                if self.resolution == (2592, 1944):
                    self.framerate = int(self.framerate / 2)
                camera.framerate = self.framerate

            camera.brightness = self.brightness
            camera.contrast = self.contrast
            camera.rotation = self.rotation
            camera.hflip = self.hflip
            camera.vflip = self.vflip

            # TODO: 조도 설정을 위한 대기시간, 최적값 테스트 필요
            sleep(2)

            # rapid capture (use_video_port = True)
            # format (jpge, png, gif, rgb, bgr, ...)
            # options : support only 'jpeg' (ex: 'quality 100')
            #camera.capture(path + im_name, im_format)
            camera.capture(save_path)

    def capture_to_opencv(self):
        iamge = None
        with PiCamera() as camera:
            '''
            Rapid capture to an OpenCV object
            'capturing to an numpy array'
            from time import sleep
            from picamera import PiCamera
            import numpy as np
            import cv2

            with PiCamera() as camera:
                camera.resolution = (320, 240)
                camera.framerate = 24
                sleep(2)
                image = np.empty((240 * 320 * 3,), dtype=np.uint8)
                camera.capture(image, 'bgr')
                image = image.reshape((240, 320, 3))
            '''
            if self.sensor_mode != 0:
                camera.sensor_mode = self.sensor_mode
            else:
                camera.resolution = self.resolution
                if self.resolution == (2592, 1944):
                    self.framerate = int(self.framerate / 2)
                camera.framerate = self.framerate

            camera.brightness = self.brightness
            camera.contrast = self.contrast
            camera.rotation = self.rotation
            camera.hflip = self.hflip
            camera.vflip = self.vflip

            sleep(2)

            image = np.empty((self.resolution[1] * self.resolution[0] * 3,), dtype=np.uint8)
            camera.capture(iamge, 'bgr')
            image = image.reshape((self.resolution[1], self.resolution[0], 3))

        return image
