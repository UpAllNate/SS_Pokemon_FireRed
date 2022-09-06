from common.ssEnums import *
from common.ssCoreImports import *
from common.ssPath import *

"""
This function opens the file hashTable.csv
and parses the hashes, saved as hex strings,
back into imagehash objects.

There are two levels of hash, 1 and 2.
These are defined as constants at the top of the program,
HASH_SIZE_LEVEL_1 and _2

If there is a collision between the observed image and multiple
LEVEL_1 hashtable instances, level 2 will be queried for a 
higher quality comparison.

Level 2 is not used imediately because they are significantly
larger hashes and therefor slower to compare / compute.
"""

class HashedImageInstance:
    def __init__(self, id : int, h : list[imagehash.ImageHash], text : str, scr : str) -> None:
        self.id = id
        self.h = h
        self.text = text
        self.scr = scr

def pokeReadHashTable() -> list: 
    h = []
    # Open table
    with open(path.file_HashTable, mode='r') as file_csv:

        # Create csv reader object of hashtable csv
        reader_obj = csv.reader(file_csv)

        c_List = {
            "ID" : None,
            "hStart" : None,
            "hEnd" : None,
            "Text" : None,
            "Screenshot" : None
        }

        for i, row in enumerate(reader_obj):
            
            # Detect the header columns
            if i == 0:
                for j, c in enumerate(row):

                    if c == "ID":
                        c_List["ID"] = j
                    if c == "hStart":
                        c_List["hStart"] = j
                    if c == "hEnd":
                        c_List["hEnd"] = j
                    if c == "Text":
                        c_List["Text"] = j
                    if c == "Screenshot":
                        c_List["Screenshot"] = j

                if None in c_List.values():
                    raise ImportError("The hash table is missing the proper headers")
                if c_List["hStart"] >= c_List["hEnd"]:
                    raise ValueError("hStart must precede hEnd")
                if c_List["hEnd"] - c_List["hStart"] + 1 != len(HASH_SIZES):
                    raise ValueError("hashTable.csv has different number of hashes than ssEnum.py/HASH_SIZES")

            # For all rows containing hash definitions
            if i >= 1:

                # For each row with a valid hash
                if row[c_List["hStart"]] != "0":

                    # Parse all hashes
                    parsedHashes = []
                    for j in range(c_List["hStart"],c_List["hEnd"] + 1): # Include hEnd column
                        parsedHashes.append(imagehash.hex_to_hash(row[j]))

                    h.append(
                        HashedImageInstance(
                            id= row[c_List["ID"]],
                            h= parsedHashes,
                            text= row[c_List["Text"]],
                            scr= row[c_List["Screenshot"]]
                        )
                    )

        logging.info(f"Hash table parsing complete; hashes parsed: {len(h)}")

        # for i, j in enumerate(h):
        #     print(f"hash {i}: {str(j.h[0])[:16]}")
    return h