from common.ssCoreImports import * # Must import first
from common.ssPath import * # Must import second
from common.ssEnums import *
from common.ssColorSets import *
from common.ssImageFunctions import *
from common.ssHashFunctions import *
from common.ssElementDetection import *

prev_playedHash_ID = -1
flatHash = 0
hashDiffFlat_Count = 0
prev_hash = None

debug_SaveDetectionImages = False

"""
Set up logging. There are two logs:
    The stream printed directly to console
    The detailed info printed to a rotating log file in common/logging.conf
"""
logging.config.fileConfig(path.file_logConfig, disable_existing_loggers=False)

hashList = pokeReadHashTable()

def playAudio(hashID):

    global prev_playedHash_ID
    prev_playedHash_ID = hashID

    print(f'triggering audio for file {hashID}')
    fileName = str(hashID) + ".wav"
    print("FileName: " + fileName)
    path_fileName = os.path.join(path.audio,fileName)
    print("FilePath: " + path_fileName)
    if os.path.exists(path_fileName):
        winsound.PlaySound(path_fileName, winsound.SND_ASYNC | winsound.SND_ALIAS )

while True:

    # Grab the screen
    screenshotWhole = ImageGrab.grab()

    if debug_SaveDetectionImages:
        screenshotWhole.save(os.path.join(path.detection,'whole.png'))

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
        if debug_SaveDetectionImages:
            croppedTextBox.save(os.path.join(path.detection, "cropped.png"))

    detectedGrey, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbGrey_Check1_V, tbGrey_Check2_H)
    if detectedGrey:
        anyDetected = True
        backgroundColor = tbGrey_Check1_V.F
        redArrowColor = RedArrow_BlueTB
        croppedTextBox = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
        if debug_SaveDetectionImages:
            croppedTextBox.save(os.path.join(path.detection, "cropped.png"))

    detectedFight, (xy_TopLeft, xy_BottomRight) = detectTextBox_1(screenshotWhole, tbFight_Check1_V, tbFight_Check2_H)
    if detectedFight:
        anyDetected = True
        backgroundColor = tbFight_Check1_V.F
        redArrowColor = RedArrow_FightTB
        croppedTextBox = screenshotWhole.crop((xy_TopLeft[0], xy_TopLeft[1], xy_BottomRight[0], xy_BottomRight[1]))
        if debug_SaveDetectionImages:
            croppedTextBox.save(os.path.join(path.detection, "cropped.png"))

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

        if debug_SaveDetectionImages:
            tbLines[0].save(os.path.join(path.detection, "line0.png"))
            tbLines[1].save(os.path.join(path.detection, "line1.png"))

        tbStripped = Image.new('RGBA', (width, tbLines[0].height + tbLines[1].height))
        tbStripped.paste(tbLines[0], (0,0))
        tbStripped.paste(tbLines[1], (0,tbLines[0].height))
        # print(f"Stripped image is \tw: {tbStripped.width}\th: {tbStripped.height}")
        if debug_SaveDetectionImages:
            tbStripped.save(os.path.join(path.detection, "lines.png"))

        # Delete the stupid red arrow from each line
        for l, im in enumerate(tbLines):

            startingRow = int(im.height * RED_ARROW_CHECK_PERCENT)
            redDetected, pixel_ColorChange = pixelScan(redArrowColor, getPixelRow(im, startingRow))

            # if l == 0:
            #     for i, p in enumerate(getPixelRow(im, startingRow)):
            #         print(f"{p[0]}\t{p[1]}\t{p[2]}")

            if redDetected:

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
        if debug_SaveDetectionImages:
            tbStripped.save(os.path.join(path.detection, "lines_redArrowRemoved.png"))

        # Break stripped TB image into four parts

        squareWidth = int(tbStripped.width / 4) - 1

        tbChunks = []
        tbChunks.append( tbStripped.crop((
                            0,
                            0,
                            squareWidth - 1,
                            tbStripped.height
                        )))
        tbChunks.append( tbStripped.crop((
                            squareWidth,
                            0,
                            squareWidth * 2 - 1,
                            tbStripped.height
                        )))
        tbChunks.append( tbStripped.crop((
                            squareWidth * 2,
                            0,
                            squareWidth * 3 - 1,
                            tbStripped.height
                        )))
        tbChunks.append( tbStripped.crop((
                            squareWidth * 3,
                            0,
                            squareWidth * 4 - 1,
                            tbStripped.height
                        )))

        tbSquare = Image.new('RGBA', (squareWidth, tbStripped.height * 4))

        y_offset = 0
        for im in tbChunks:
            tbSquare.paste(im, (0,y_offset))
            y_offset += im.size[1]

        if debug_SaveDetectionImages:
            tbSquare.save(os.path.join(path.detection, "square.png"))

        # Process hash of square textbox image
        new_hash = imagehash.dhash(tbSquare, HASH_SIZES[0])

        if prev_hash is None:
            prev_hash = new_hash

        diff = new_hash - prev_hash
        prev_hash = new_hash

        # Monitor when the text box is steady,
        # Meaning new characters are not rolling out
        if diff > FLATHASH_THRESHOLD:
            hashDiffFlat_Count = 0
        else:
            hashDiffFlat_Count += 1

        if hashDiffFlat_Count >= FLATHASH_COUNTGOAL:
            flatHash = True
        else:
            flatHash = False

        print(f"new: {str(new_hash)[0:10]}, prev:{str(prev_hash)[0:10]}, diff: {diff}, count: {hashDiffFlat_Count}, flat = {flatHash}")

        if flatHash:

            hashMatchID = None

            # First pass search
            pass1_Matches = []
            for i, x in enumerate(hashList):
                if x.h[0] - new_hash <= HASH_TOLERANCES[0]:
                    pass1_Matches.append(i)

            if len(pass1_Matches) == 1:
                hashMatchID = pass1_Matches[0]

            else:

                new_hash = imagehash.dhash(tbSquare, HASH_SIZES[1])
                # Second pass search
                pass2_Matches = []
                for i in pass1_Matches:
                    if hashList[i] - new_hash <= HASH_TOLERANCES[1]:
                        pass2_Matches.append(i)

                if len(pass2_Matches) == 1:
                    hashMatchID = pass2_Matches[0]

                else:

                    new_hash = imagehash.dhash(tbSquare, HASH_SIZES[2])
                    # Second pass search
                    pass3_Matches = []
                    for i in pass2_Matches:
                        if hashList[i] - new_hash <= HASH_TOLERANCES[2]:
                            pass3_Matches.append(i)

                    if len(pass3_Matches) == 1:
                        hashMatchID = pass3_Matches[0]

            if hashMatchID is not None and hashMatchID != prev_playedHash_ID:
                playAudio(hashMatchID)
                prev_playedHash_ID = hashMatchID

        else:
            hashMatchID = None

    else:
        flatHash = 0
        hashDiffFlat_Count = 0
        hashMatchID = None