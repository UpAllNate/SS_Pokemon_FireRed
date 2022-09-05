import os
import csv
import imagehash
from pathlib import Path as pathFunction
import logging
import logging.config
import pyautogui
from PIL import Image, ImageGrab
from enum import Enum, auto as enumAuto

PIXEL_COLOR_TOLERANCE = 0
VERTICAL_FIRST_MODE = False
HORIZONTAL_FIRST_MODE = True

"""
Get directory and file paths
"""
class path:
    dir = os.path.dirname(os.path.realpath(__file__))
    common = os.path.join(dir,'common')
    reference = os.path.join(common,'reference')
    audio = os.path.join(common,'audio')

    file_logConfig = os.path.join(common,'logging.conf')
    file_HashTable = os.path.join(common,'hashTable.csv')
    file_blueTop = os.path.join(reference,'blue_Top.png')
    file_fightTop = os.path.join(reference,'fight_Top.png')
    file_greyTop = os.path.join(reference,'grey_Top.png')
    file_redArrow_refWhite = os.path.join(reference,'redArrow_refWhite.png')
    file_redArrow_refBlue = os.path.join(reference,'redArrow_refBlue.png')
    file_redArrow_eraseWhite = os.path.join(reference,'redArrow_eraseWhite.png')
    file_redArrow_eraseBlue = os.path.join(reference,'redArrow_eraseBlue.png')

# Validate all required directories are present
dirs = []
dirs.append(path.common)
dirs.append(path.reference)
dirs.append(path.audio)

for dir in dirs:
    p = pathFunction(dir)
    if not p.is_dir:
        raise ImportError(f"Required directory missing at: {dir}")

# Validate all required files are present
files = []
files.append(path.file_logConfig)
files.append(path.file_HashTable)
files.append(path.file_blueTop)
files.append(path.file_fightTop)
files.append(path.file_greyTop)
files.append(path.file_redArrow_refWhite)
files.append(path.file_redArrow_refBlue)
files.append(path.file_redArrow_eraseWhite)
files.append(path.file_redArrow_eraseBlue)

for file in files:
    p = pathFunction(file)
    if not p.is_file:
        raise ImportError(f"Required file missing at: {file}")

"""
Set up logging. There are two logs:
    The stream printed directly to console
    The detailed info printed to a rotating log file in common/logging.conf
"""
logging.config.fileConfig(path.file_logConfig, disable_existing_loggers=False)

class EnumDetectState(Enum):
    init = enumAuto()
    outer_1 = enumAuto()
    inner_1 = enumAuto()
    fill = enumAuto()
    inner_2 = enumAuto()
    outer_2 = enumAuto()

class DE_ColorSet:
    def __init__(self,
        O1 : tuple[int,int,int], I1 : tuple[int,int,int],
        F : tuple[int,int,int],
        I2 : tuple[int,int,int], O2 : tuple[int,int,int]) -> None:
            self.O1 = O1
            self.I1 = I1
            self.F = F
            self.I2 = I2
            self.O2 = O2

"""
In the following section, the detectable Element colors are defined:

Blue Textbox
Grey Textbox
Fight Textbox

--- More will be added as this program's functionality is expanded
"""

"""Blue"""
# These colors correspond to the sequence expected for the middle-body of a blue dialogue text box
tbBlue_Check1_V = DE_ColorSet(
    O1 =   (72, 112, 160),
    I1 =   (160, 208, 224),
    F =    (248,248,248),
    I2 =   (160, 208, 224),
    O2 =   (72, 112, 160)
)

# These colors correspond to the sequence expected for the top-pixel edge of a blue dialog text box.
# This is desirable because it gives us the starting X-Coordinate for the full text box
tbBlue_Check2_H = DE_ColorSet(
    O1 =   (160, 208, 224),
    I1 =   (208, 224, 240),
    F =    (248,248,248),
    I2 =   (208, 224, 240),
    O2 =   (160, 208, 224)
)

"""Grey"""
# These colors correspond to the sequence expected for the middle-body of a grey dialogue text box
tbGrey_Check1_V = DE_ColorSet(
    O1 =   (104, 112, 120),
    I1 =   (200, 200, 216),
    F =    (248, 248, 248),
    I2 =   (200, 200, 216),
    O2 =   (104, 112, 120)
)

# The same check is used because the horizontal scan colors are the same
tbGrey_Check2_H = tbGrey_Check1_V

"""Fight"""
# These colors correspond to the sequence expected for the middle-body of a fight dialogue text box
tbFight_Check1_V = DE_ColorSet(
    O1 =   (200, 168, 72),
    I1 =   (224, 216, 224),
    F =    (40, 80, 104),
    I2 =   (224, 216, 224),
    O2 =   (200, 168, 72)
)

# The same check is used because the horizontal scan colors are the same
tbFight_Check2_H = tbFight_Check1_V

# State machine, returns detection result, fill start pixel, fill end pixel
def pixelScan(colors : DE_ColorSet, pixels : list[tuple[int,int,int]]) -> tuple[bool, list]:

    detectState = EnumDetectState.init
    pixel_ColorChange = []

    for i, pix in enumerate(pixels):
        if detectState == EnumDetectState.init:

            if colors.O1 == pix:
                # print("Found Outer 1")
                detectState = EnumDetectState.outer_1
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)

        if detectState == EnumDetectState.outer_1:

            if colors.I1 == pix:
                detectState = EnumDetectState.inner_1
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)
            elif pix != colors.O1 and pix != colors.I1:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.inner_1:

            if colors.F == pix:
                detectState = EnumDetectState.fill
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)
            elif pix != colors.I1 and pix != colors.F:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.fill:

            if colors.I2 == pix:
                detectState = EnumDetectState.inner_2
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)
            # There is no wrong-color-recovery for fill, because the
            # element contents are assumed to be complex (like various text characters)

        if detectState == EnumDetectState.inner_2:

            if colors.O2 == pix:
                detectState = EnumDetectState.outer_2
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)
            elif pix != colors.I2 and pix != colors.O2:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.outer_2:

            if colors.O2 != pix:
                pixel_ColorChange.append(i)
                # print(pixel_ColorChange)
                break
        
    if detectState == EnumDetectState.outer_2:
        pixel_ColorChange.append(len(pixels))
        
    return detectState == EnumDetectState.outer_2, pixel_ColorChange

# Takes screenshot, returns success/failure bool and X0, Y0, Width, Height tuple
def detectTextBox_1(screenshot : Image, colorsV : DE_ColorSet, colorsH : DE_ColorSet) -> tuple[bool, tuple[int,int,int,int]]:
    X0 = 0
    Y0 = 0
    X1 = 0
    Y1 = 0
    detected = False

    # Step 1: Scan for pixels on virtical centerline of monitor
    column = int(screenshot.size[0] / 2)
    pixelList = [screenshot.getpixel((column, i)) for i in range(screenshot.size[1])]
    success, pixel_ColorChange = pixelScan(colorsV, pixelList)

    if success:
        Y0 = pixel_ColorChange[2]
        Y1 = pixel_ColorChange[3] - 1 # Don't want to crop the first pixel row of frame

        # Step 2: Scan for pixels on top row of the image
        row = Y0
        success, pixel_ColorChange = pixelScan(colorsH, [screenshot.getpixel((i, row)) for i in range(screenshot.size[0])])

        if success:
            X0 = pixel_ColorChange[2]
            X1 = pixel_ColorChange[3] - 1
            detected = True
    
    # Detected bool, (x,y) top left corner, width, height
    return detected, ((X0, Y0), (X1, Y1))

class color_fightMenu:
    outer = (112, 104, 128)
    inner = (2166, 208, 216)
    fill = (248, 248, 248)


"""
This function opens the file hashTable.csv
and parses the hashes, saved as hex strings,
back into imagehash objects.
"""
def pokeReadHashTable() -> list: 
    h = []
    # Open table
    with open(path.file_HashTable, mode='r') as file_csv:
        reader_obj = csv.reader(file_csv)
        for row in reader_obj:
            if row[1] != "0":
                h.append(imagehash.hex_to_hash(row[1]))
        logging.info(f"Hash table parsing complete; hashes parsed: {len(h)}")
    return h

hashList = pokeReadHashTable()

while True:

    # Grab the screen
    screenshotWhole = ImageGrab.grab()

    detected, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbBlue_Check1_V, tbBlue_Check2_H)
    if detected:
        croppedBlue = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))

    detected, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbGrey_Check1_V, tbGrey_Check2_H)
    if detected:
        croppedBlue = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))

    detected, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbFight_Check1_V, tbFight_Check2_H)
    if detected:
        croppedBlue = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
