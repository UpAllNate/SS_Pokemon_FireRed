import os
import csv
import imagehash
from pathlib import Path as pathFunction
import logging
import logging.config
import pyautogui
from PIL import Image, ImageChops
from enum import Enum, auto as enumAuto

class boxDetectState(Enum):
    init = enumAuto()
    outer_1 = enumAuto()
    inner_1 = enumAuto()
    fill = enumAuto()
    inner_2 = enumAuto()
    outer_2 = enumAuto()

class color_terminalBlock_Grey:
    outer = (104, 112, 120)
    inner = (200, 200, 216)
    fill = (248, 248, 248)

class color_terminalBlock_Blue:
    outer = (72, 112, 160)
    inner = (160, 208, 224)
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
    screenshotWhole = pyautogui.screenshot()

    blueDetectionState = boxDetectState.init
    greyDetectionState = boxDetectState.init
    fightDetectionState = boxDetectState.init

    # Search for any of the three text box types by scanning
    # the column of pixels at screen center
    x = screenshotWhole.width / 2
    for i in range(screenshotWhole.height):
        pix = screenshotWhole.getpixel((x,i))

        

