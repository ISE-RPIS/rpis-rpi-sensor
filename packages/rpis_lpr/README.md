# License Plate Recognition (LPR) for RPIS
## Required
- Python 3.7 recommended
- OpenCV
- pytesseract
- numpy

## Using libraries
- cv2
- numpy
- pytesseract
- platform

## How to use ?
```
from rpis_lpr.LPR import LPR

# 1. using path
img_path = 'path/of/your/image'
license_char = LPR().get_license_plate_char(img_path)


# 2. using numpy.ndarray
img_ndarray # some img object like numpy.ndarray type
license_char = LPR().get_license_plate_char(img_ndarray)


print(license_char)
# 12가3456
```

## Important
Recommended using an image like:
- License plate width is 500px above in image.
- Just one-line text plate.
