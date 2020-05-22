# Camera for RPIS
## Required
- Python 3.7 recommended
- picamera
- OpenCV

## Using libraries
- picamera
- cv2
- numpy
- time, platform, os

## How to install ?
Copy 'rpis_camera' directory into 'site-packages' directory, below 'python/lib'.

## How to use ?
```
from rpis_camera.camera import Camera

camera = Camera()

# setting options
camera.resolution = (1920, 1080)
camera.framerate = 30

# capture using path
# img_name must be included formatter!
camera.capture(path='~', img_name='capture.jpg')

# capture to OpenCV object (numpy.ndarray type)
image = camera.capture_to_opencv()
```
