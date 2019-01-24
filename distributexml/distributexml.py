import pprint
import os
import glob
import shutil
import argparse
import logging
import sys


argparser = argparse.ArgumentParser(description="Distribute MODS xml files into serials issues -- for YWCA project")
argparser.add_argument('XMLFILESDIR', help="Source: The name of a directory full of xml files titled by the same name as their destination issue directory. e.g. myxmlfilesdir/smith_ssc_324_am_v002_n012.xml")
argparser.add_argument('TITLEBATCHDIR', help="Destination: The name of a directory full of issue directories.")
argparser.add_argument('--dry-run', action='store_true', help="Print out what I would do, but don't actually do it")
cliargs = argparser.parse_args()

XMLFILESDIR = cliargs.XMLFILESDIR

if cliargs.dry_run is True:
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)
else:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)


xmlFileList = glob.glob(XMLFILESDIR + "/*.xml")
if len(xmlFileList) > 0:
    for xmlFilePathName in xmlFileList:
        xmlFileBaseName = os.path.basename(xmlFilePathName)
        issueFolder = cliargs.TITLEBATCHDIR + '/' + xmlFileBaseName.split('.')[0]
        logging.debug("xmlFilePathName: %s" % xmlFilePathName)
        logging.debug("issueFolder: %s" % issueFolder)
        cpSource = xmlFilePathName
        cpDestination = "%s/MODS.xml" % issueFolder
        logging.debug("cpSource: %s" % cpSource)
        logging.debug("cpDestination: %s" % cpDestination)
        try:
            if cliargs.dry_run is False:
                shutil.copyfile(cpSource, cpDestination)
        except FileNotFoundError as e:
            logging.error(e)
        logging.info(cpDestination)
else:
    logging.error("No xml files found in %s" % XMLFILESDIR)
    exit(1)
