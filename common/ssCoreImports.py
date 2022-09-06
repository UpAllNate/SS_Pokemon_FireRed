import os
import csv
import imagehash
from pathlib import Path as pathFunction
import logging
import logging.config
from PIL import Image, ImageGrab
from enum import Enum, auto as enumAuto
import winsound