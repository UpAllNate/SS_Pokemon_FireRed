from common.ssColorSets import *
from common.ssEnums import *

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