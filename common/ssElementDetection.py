from common.ssCoreImports import *
from common.ssImageFunctions import *

# Takes screenshot, returns success/failure bool and X0, Y0, Width, Height tuple
def detectTextBox_1(screenshot : Image, colorsV : DE_ColorSet, colorsH : DE_ColorSet) -> tuple[bool, tuple[int,int,int,int]]:
    X0 = 0
    Y0 = 0
    X1 = 0
    Y1 = 0
    detected = False

    # Step 1: Scan for pixels on virtical centerline of monitor
    pixelList = getPixelColumn(screenshot,int(screenshot.width / 2))
    success, pixel_ColorChange = pixelScan(colorsV, pixelList)

    if success:
        Y0 = pixel_ColorChange[2]
        Y1 = pixel_ColorChange[3] - 1 # Don't want to crop the first pixel row of frame

        # Step 2: Scan for pixels on top row of the image
        success, pixel_ColorChange = pixelScan(colorsH, getPixelRow(screenshot,Y0))

        if success:
            X0 = pixel_ColorChange[2]
            X1 = pixel_ColorChange[3] - 1
            detected = True
    
    # Detected bool, (x,y) top left corner, width, height
    return detected, ((X0, Y0), (X1, Y1))