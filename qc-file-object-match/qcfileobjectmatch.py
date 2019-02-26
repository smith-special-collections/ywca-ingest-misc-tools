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

if __name__ == "__main__":
    "Main function"
    objectIds = getObjectIdsFromFile(fileListFile)
    oddBalls = list(filter(lambda x: '.' in x, objectIds))
    logging.warning("These oddball IDs look suspicious: %s" % oddBalls)
    for objectId in objectIds:
        digitalObjects = findObjects(objectId)
        if len(digitalObjects) == 1:
            logging.info("One matching object found %s %s" % (objectId, objects[0]['PID']) )
        if len(digitalObjects) < 1:
            logging.error("No matching object found %s" % objectId)
        if len(digitalObjects) > 1:
            logging.error("More than one object found %s" % objectId)
