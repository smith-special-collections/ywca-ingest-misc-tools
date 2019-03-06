description = """This tool takes a list of object files and looks for them on
Compass. If it doesn't find a matching object, or if it finds more than one
object, it returns an error. The local id of the object is derivied from the
file naming pattern. This id is used to query the mods_identifier_local_s field
in Solr."""

import requests
import logging
import argparse
import sys
import os

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument('FILELISTFILE', help="location of a text file listing one object file per line.")
argparser.add_argument('--output-file-base', help="I supplied write reports about missing objects, dupes etc. A base name to make output file names from.")
cliargs = argparser.parse_args()

fileListFile = cliargs.FILELISTFILE

logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

solr_query_template = "http://compass-fedora-prod.fivecolleges.edu:8080/solr/collection1/select?q=mods_identifier_local_s%3A%22{local_id}%22&fl=PID%2Cfgs_label_s%2Cmods_titleInfo_partName_s%2Cmods_titleInfo_title_s&wt=json&indent=true"

def getObjectIdsFromFile(fileListFile):
    objectIds = []
    with open(fileListFile) as fp:
        for line in fp:
            local_id = os.path.basename(line.strip())
            local_id = local_id.replace(".TIF","").replace(".tif", "")
            logging.debug(local_id)
            objectIds.append(local_id)
    return objectIds

def findObjects(objectId):
    query = solr_query_template.format(local_id = objectId)
    logging.debug(query)
    response = requests.get(query)
    logging.debug(response)
    responseData = response.json()
    digitalObjects = responseData['response']['docs']
    return digitalObjects

def writeObjectsToFile(myFileName, myList):
    with open(myFileName, 'w') as fp:
        for myItem in myList:
            fp.write(myItem + '\n')

def pages2topLevelObjects(pages):
    topLevelObjects = []
    for page in pages:
        splitId = page.split("_")
        splitId.pop(-1)
        topLevelObjects.append('_'.join(splitId))
    topLevelObjects = set(topLevelObjects)
    return topLevelObjects

if __name__ == "__main__":
    "Main function"
    objectIds = getObjectIdsFromFile(fileListFile)
    oddBalls = list(filter(lambda x: '.' in x, objectIds))
    if len(oddBalls) > 0:
        logging.warning("These oddball IDs look suspicious: %s" % oddBalls)
    missingObjects = []
    dupeObjects = []
    for objectId in objectIds:
        digitalObjects = findObjects(objectId)
        if len(digitalObjects) == 1:
            logging.info("One matching object found %s %s" % (objectId, digitalObjects[0]['PID']) )
        if len(digitalObjects) < 1:
            logging.error("No matching object found %s" % objectId)
            missingObjects.append(objectId)
        if len(digitalObjects) > 1:
            logging.error("More than one object found %s" % objectId)
            dupeObjects.append(objectId)

    missingTopLevelObjects = pages2topLevelObjects(missingObjects)
    
#    import pdb; pdb.set_trace()
    
    if cliargs.output_file_base:
        missingFilename = cliargs.output_file_base + '-missing.log'
        print("Writing missing itemes to %s" % missingFilename)
        writeObjectsToFile(missingFilename, missingObjects)

        dupeFilename = cliargs.output_file_base + '-dupes.log'
        print("Writing dupe items to %s" % dupeFilename)
        writeObjectsToFile(dupeFilename, dupeObjects)

        missingTopsFilename = cliargs.output_file_base + '-missing-tlos.log'
        print("Writing dupe items to %s" % missingTopsFilename)
        writeObjectsToFile(missingTopsFilename, missingTopLevelObjects)
