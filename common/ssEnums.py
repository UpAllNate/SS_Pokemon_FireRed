from common.ssCoreImports import *

HASH_SIZES = (16, 24, 32)
RED_ARROW_CHECK_PERCENT = 0.4

HASH_TOLERANCES = (10, 10, 10)

FLATHASH_THRESHOLD = 2
FLATHASH_COUNTGOAL = 8

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