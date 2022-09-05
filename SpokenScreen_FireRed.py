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

class EnumFightBoxRowPercentage():
    Line1_Start =   0.1761904762
    Line1_End =     0.4380952381
    Line2_Start =   0.6523809524
    Line2_End =     0.9142857143

class EnumBlueBoxRowPercentage():
    Line1_Start =   0.1696428571
    Line1_End =     0.4151785714
    Line2_Start =   0.5848214286
    Line2_End =     0.8303571429

RED_ARROW_CHECK_PERCENT = 0.25

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
RedArrows

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

"""Red Arrows"""
RedArrow_BlueTB = DE_ColorSet(
    O1 =   (248, 248, 248),
    I1 =   (96, 96, 96),
    F =    (224, 0, 0),
    I2 =   (96, 96, 96),
    O2 =   (248, 248, 248)
)

RedArrow_FightTB = DE_ColorSet(
    O1 =   (40, 80, 104),
    I1 =   (40, 48, 48),
    F =    (248, 0, 0),
    I2 =   (40, 48, 48),
    O2 =   (40, 80, 104)
)

def getPixelRow(im : Image, row : int) -> list[tuple[int,int,int]]:
    return [im.getpixel((i, row)) for i in range(im.width)]

def getPixelColumn(im : Image, column : int) -> list[tuple[int,int,int]]:
    return [im.getpixel((column, i)) for i in range(im.height)]

# State machine, returns detection result, fill start pixel, fill end pixel
def pixelScan(colors : DE_ColorSet, pixels : list[tuple[int,int,int]]) -> tuple[bool, list]:

    detectState = EnumDetectState.init

    for i, pix in enumerate(pixels):
        if detectState == EnumDetectState.init:

            pixel_ColorChange = []

            if colors.O1 == pix:
                detectState = EnumDetectState.outer_1
                pixel_ColorChange.append(i)

        if detectState == EnumDetectState.outer_1:

            if colors.I1 == pix:
                detectState = EnumDetectState.inner_1
                pixel_ColorChange.append(i)
            elif pix != colors.O1 and pix != colors.I1:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.inner_1:

            if colors.F == pix:
                detectState = EnumDetectState.fill
                pixel_ColorChange.append(i)
            elif pix != colors.I1 and pix != colors.F:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.fill:

            if colors.I2 == pix:
                detectState = EnumDetectState.inner_2
                pixel_ColorChange.append(i)
            # There is no wrong-color-recovery for fill, because the
            # element contents are assumed to be complex (like various text characters)

        if detectState == EnumDetectState.inner_2:

            if colors.O2 == pix:
                detectState = EnumDetectState.outer_2
                pixel_ColorChange.append(i)
            elif pix != colors.I2 and pix != colors.O2:
                detectState = EnumDetectState.init

        if detectState == EnumDetectState.outer_2:

            if colors.O2 != pix:
                pixel_ColorChange.append(i)
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

    """
    This section of the code checks for a blue, grey, or fight text box.
    If any is detected, the cropped text will be saved in croppedTextBox
    for further processing
    """
    anyDetected = False

    detectedBlue, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbBlue_Check1_V, tbBlue_Check2_H)
    if detectedBlue:
        anyDetected = True
        backgroundColor = tbBlue_Check1_V.F
        redArrowColor = RedArrow_BlueTB
        croppedTextBox = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
        croppedTextBox.save("S:\\text\\Blue_Cropped.png")

    detectedGrey, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbGrey_Check1_V, tbGrey_Check2_H)
    if detectedGrey:
        anyDetected = True
        backgroundColor = tbGrey_Check1_V.F
        redArrowColor = RedArrow_BlueTB
        croppedTextBox = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
        croppedTextBox.save("S:\\text\\Grey_Cropped.png")

    detectedFight, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbFight_Check1_V, tbFight_Check2_H)
    if detectedFight:
        anyDetected = True
        backgroundColor = tbFight_Check1_V.F
        redArrowColor = RedArrow_FightTB
        croppedTextBox = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
        croppedTextBox.save("S:\\text\\Fight_Cropped.png")

    if detectedBlue or detectedGrey:
        Line1_Start = EnumBlueBoxRowPercentage.Line1_Start
        Line1_End = EnumBlueBoxRowPercentage.Line1_End
        Line2_Start = EnumBlueBoxRowPercentage.Line2_Start
        Line2_End = EnumBlueBoxRowPercentage.Line2_End
    
    if detectedFight:
        Line1_Start = EnumFightBoxRowPercentage.Line1_Start
        Line1_End = EnumFightBoxRowPercentage.Line1_End
        Line2_Start = EnumFightBoxRowPercentage.Line2_Start
        Line2_End = EnumFightBoxRowPercentage.Line2_End
    
    if anyDetected:
        
        width = croppedTextBox.width
        height = croppedTextBox.height

        # Crop out the two lines of text to maximize information density
        tbLines = []
        tbLines.append(
            croppedTextBox.crop((
                0,
                height * Line1_Start,
                width,
                height * Line1_End
                ))
            )
        tbLines.append(
            croppedTextBox.crop((
                0,
                height * Line2_Start,
                width,
                height * Line2_End
                ))
            )

        tbStripped = Image.new('RGBA', (width, tbLines[0].height + tbLines[1].height))
        tbStripped.paste(tbLines[0], (0,0))
        tbStripped.paste(tbLines[1], (0,tbLines[0].height))
        # print(f"Stripped image is \tw: {tbStripped.width}\th: {tbStripped.height}")
        tbStripped.save("S:\\Text\\BeforeRedArrowRemoval.png")

        # Delete the stupid red arrow from each line
        for im in tbLines:

            startingRow = int(im.height * RED_ARROW_CHECK_PERCENT)
           
            redDetected, pixel_ColorChange = pixelScan(redArrowColor, getPixelRow(im, startingRow))
            
            if redDetected:

                # print("Red Detected")

                # print(pixel_ColorChange)
                
                startingColumn = pixel_ColorChange[1]
                edgeFound = False # Initialize

                # Find the top edge of the red arrow
                offset = 1
                while not edgeFound:
                    nextRow = startingRow - offset

                    # If we get to the top edge of the image, that's the edge
                    if nextRow < 0:
                        edgeFound = True
                        edge_Y = 0
                
                    # If we hit background color, we found the edge on the last pixel
                    elif im.getpixel((startingColumn, nextRow)) == backgroundColor:
                        edgeFound = True
                        edge_Y = nextRow + 1

                    # Increment to look at the next pixel going upward
                    offset = offset + 1
                
                # Find the left edge of the red arrow
                offset = 1
                edgeFound = False
                while not edgeFound:
                    nextColumn = startingColumn - offset

                    # If we get to the top edge of the image, that's the edge
                    if nextColumn < 0:
                        raise ValueError("Didn't find arrow left edge")
                
                    # If we hit background color, we found the edge on the last pixel
                    elif im.getpixel((nextColumn, edge_Y)) == backgroundColor:
                        edgeFound = True
                        edge_X = nextColumn + 1

                    # Increment to look at the next pixel going upward
                    offset = offset + 1
 
                # print(f"top left coordinate is: ({edge_X},{edge_Y})")
                # print(f"Detected pixel is color: {im.getpixel((edge_X, edge_Y))}")
                
                allComplete_X = False
                currentX = edge_X
                offset_X = 0
                while not allComplete_X:

                    allComplete_Y = False
                    currentY = edge_Y
                    offset_Y = 0
                    while not allComplete_Y:

                        # print(f"({currentX},{currentY})")

                        if im.getpixel((currentX, currentY)) == backgroundColor:
                            allComplete_Y = True
                        else:
                            im.putpixel((currentX, currentY), (backgroundColor[0], backgroundColor[1], backgroundColor[2], 255))
                        
                        currentY = currentY + 1

                    currentX = currentX + 1

                    if im.getpixel((currentX,edge_Y)) == backgroundColor:
                        allComplete_X = True
        
        tbStripped = Image.new('RGBA', (width, tbLines[0].height + tbLines[1].height))
        tbStripped.paste(tbLines[0], (0,0))
        tbStripped.paste(tbLines[1], (0,tbLines[0].height))
        print(f"Stripped image is \tw: {tbStripped.width}\th: {tbStripped.height}")
        tbStripped.save("S:\\Text\\Stripped.png")