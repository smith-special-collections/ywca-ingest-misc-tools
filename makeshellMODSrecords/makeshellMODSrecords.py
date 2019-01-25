description = """For each object directory create a MODS.xml file.

Example:
smith_ssc_324_digital_object_200/
    MODS.xml
smith_ssc_324_digital_object_257/
    MODS.xml
smith_ssc_324_digital_object_323/
    MODS.xml

The MODS file will set the title and local id as the directory name.
"""
import shutil, os
import glob
import argparse
from argparse import RawTextHelpFormatter
from pprint import pprint

argparser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
argparser.add_argument("TOPFOLDER")
argparser.add_argument("SEARCHPATTERN", help="Example 'smith*' MUST BE IN QUOTES")
argparser.add_argument('--nocopy', help="Modifying the folder directly instead of making a copy", action="store_true")
args = argparser.parse_args()

TOPFOLDER = args.TOPFOLDER

sourceFolder = TOPFOLDER.strip().strip('/')

# MODS template for page level metadata (just ID for linking)
pageModsTemplate = """<?xml version="1.0" encoding="UTF-8"?>
<mods xmlns="http://www.loc.gov/mods/v3" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">
    <titleInfo>
        <title>{identifier}</title>
    </titleInfo>
    <identifier type="local">{identifier}</identifier>
</mods>
"""

if __name__ == "__main__":
    if(args.nocopy):
        destFolder = sourceFolder
    else:
        destFolder = sourceFolder + '-batched'
        shutil.copytree(sourceFolder, destFolder)
    os.chdir(destFolder)

    dirList = glob.glob(args.SEARCHPATTERN + '/')
    for dir in dirList:
        id = dir.strip('/')
        modsOutput = pageModsTemplate.format(identifier=id)
        modsFileName = dir + '/MODS.xml'
        print("Generating %s" % modsFileName)
        with open(modsFileName, 'w') as modsFile:
            modsFile.write(modsOutput)
