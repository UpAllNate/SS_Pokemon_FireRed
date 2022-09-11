
from common.ssCoreImports import *
from common.ssHashFunctions import *

"""
Get directory and file paths
"""
class path:

    # Directories
    dir = os.path.dirname(os.path.realpath(__file__))[:-7] # The -7 deletes '\common' from the string returned
    common = os.path.join(dir,'common')
    reference = os.path.join(common,'reference')
    AudioPacks = os.path.join(common,'AudioPacks')
    screenshot = os.path.join(common, 'screenshot')
    detection = os.path.join(screenshot, 'detection')
    logShots = os.path.join(screenshot,'logShots')

    # Files
    file_logConfig = os.path.join(common,'logging.conf')
    file_HashTable = os.path.join(common,'hashTable.csv')
    
    # Built on script startup
    selectedAudioPack = None

# Verify that path is within \common\
p = pathFunction(path.dir)
if not p.is_dir:
    raise ImportError("Expected ssPath.py within ...\\common\\")

# Validate all required directories are present
dirs = []
dirs.append(path.common)
dirs.append(path.reference)
dirs.append(path.AudioPacks)
dirs.append(path.screenshot)
dirs.append(path.detection)
dirs.append(path.logShots)

for dir in dirs:
    p = pathFunction(dir)
    if not p.is_dir:
        raise ImportError(f"Required directory missing at: {dir}")

# Validate all required files are present
files = []
# files.append(path.file_logConfig)

for file in files:
    p = pathFunction(file)
    if not p.is_file:
        raise ImportError(f"Required file missing at: {file}")