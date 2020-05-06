# License Plate Recognition (LPR)
## Required
- Python 3.7 recommended
- OpenCV
- Pytesseract
- Numpy

## How to use?
If you give a path of image, finding and returing text of license plate.
```
from LPR import LPR

img_path = 'path/of/your/image'
license_char = LPR.getLicensePlateChar(img_path)

print(license_char)
# 12가3456
```

## Important
Recommended using an image like:
- License plate width is 500px above in image.
- Just one-line text plate.
