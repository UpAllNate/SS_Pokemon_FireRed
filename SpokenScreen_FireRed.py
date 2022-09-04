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

tbBlue_Check1_V = DE_ColorSet(
    VO1 =   (72, 112, 160),
    VI1 =   (160, 208, 224),
    VF =    (248,248,248)
    VI2 =   (160, 208, 224),
    VO2 =   (72, 112, 160)
)





# State machine, returns detection result, fill start pixel, fill end pixel
def pixelScan_ByPercent(self, colors : DE_ColorSet, pixels : list[tuple[int,int,int]]) -> tuple(bool, int, int):

    detectState = EnumDetectState.init

    for i, pix in enumerate(pixels):
        if detectState == EnumDetectState.init:

            if colors.O1 == pix:
                detectState = EnumDetectState.outer_1

        if detectState == EnumDetectState.outer_1:

            if colors.I1 == pix:
                detectState = EnumDetectState.inner_1
            elif pix != colors.O1 and pix != colors.I1:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.inner_1:

            if colors.F == pix:
                detectState = EnumDetectState.fill
                fillStart = i
            elif pix != colors.I1 and pix != colors.F:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.fill:

            if colors.I2 == pix:
                detectState = EnumDetectState.inner_2
                fillEnd = i - 1
            # There is no wrong-color-recovery for fill, because the
            # element contents are assumed to be complex (like various text characters)

        if detectState == EnumDetectState.inner_2:

            if colors.O2 == pix:
                detectState = EnumDetectState.outer_2
                break
            elif pix != colors.I2 and pix != colors.O2:
                detectState = EnumDetectState.init
        
    return detectState, fillStart, fillEnd

class DetectableElement:

    # The colors are all tuples of length 3, for RGB
    def __init__(self) -> None:
        self.detected = False

    # This state machine scans for the color markers of a detectable element
    def detectElement(self, scanMode : bool, percentW : float, percentH : float, screenshot : Image):

        ss_W, ss_H = screenshot.size()

        if percentW > 1.0 or percentW <= 0.0:
            msg = f"Cannot set percentW to {percentW}"
            logging.fatal(msg)
            raise ValueError(msg)

        if percentH > 1.0 or percentH <= 0.0:
            msg = f"Cannot set percentH to {percentH}"
            logging.fatal(msg)
            raise ValueError(msg)

        # Scan for element across vertical and horizontal pixel lines
        if scanMode == VERTICAL_FIRST_MODE:

            index_pixelColumn = ss_W * percentW
            pixels = [screenshot.getpixel(index_pixelColumn,i) for i in range(ss_H)]

            success, self.fill_Y0, self.fill_Y1 = self.pixelScan(self.colors[0],pixels)

            if success:
                index_pixelRow = percentH * (self.fill_Y1 - self.fill_Y0) + self.fill_Y0
                pixels = [screenshot.getpixel(i,index_pixelRow) for i in range(ss_W)]

                return self.pixelScan(self.colors[1],pixels)
        
        else:

            index_pixelRow = ss_H * percentH
            pixels = [screenshot.getpixel(i,index_pixelRow) for i in range(ss_W)]

            success, self.fill_X0, self.fill_X1 = self.pixelScan(self.colors[1],pixels)

            if success:
                index_pixelColumn = percentW * (self.fill_X1 - self.fill_X0) + self.fill_X0
                pixels = [screenshot.getpixel(index_pixelColumn,i) for i in range(ss_H)]

                return self.pixelScan(self.colors[0],pixels)



class color_terminalBlock_Grey:
    outer = (104, 112, 120)
    inner = (200, 200, 216)
    fill = (248, 248, 248)


class color_terminalBlock_Fight:
    outer = (200, 168, 72)
    inner = (224, 216, 224)
    fill = (40, 80, 104)

class color_fightMenu:
    outer = (112, 104, 128)
    inner = (2166, 208, 216)
    fill = (248, 248, 248)

# Get directory and file paths
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
