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

## Properties
>resolution (tuple) : Set camera resolution
```
camera.resolution = (1920, 1440)
```
>framerate (int) : Set camera framerate
```
camera.framerate = 60
```
>brightness (int) : Set camera brightness, default 50
```
camera.brightness = 50
```
>contrast (int) : Set camera contrast, default 0
```
camera.contrast = 50
```
>rotation (0, 90, 180, 270) : Set camera rotation, default 0
```
camera.rotation = 180
```
>hflip (bool) : Set camera horizontal flip, default false
```
camera.hflip = True
```
>vflip (bool) : Set camera vertical flip, default false
```
camera.vflip = True
```
>sensor_mode (0~7) : Set camera sensor_mode, default 0(auto) <br/>
>※ If you set this, don't set 'resolution' and 'framerate'.
```
camera.sensor_mode = 6
```
*(v2 Module)*
| Mode | Resolution | Ratio | FPS | Image Size |
| ----- | ----- | ----- | ----- | ----- |
| 0 | Auto | Auto | Auto | Auto |
| 1 | 1920x1080 | 16:9 | fps<=30 | Partial |
| 4 | 1640x1232 | 4:3 | fps<=40 | Full |
| 5 | 1640x922 | 16:9 | fps<=40 | Full |
| 6 | 1280x720 | 16:9 | 40<fps<=90 | Partial |
| 7 | 640x480 | 4:3 | 40<fps<=90 | Partial |
