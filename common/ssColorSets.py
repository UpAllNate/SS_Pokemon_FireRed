from common.ssCoreImports import *

# Detectable Element Color Set
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
    F =    (224, 8, 8),
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

class color_fightMenu:
    pass