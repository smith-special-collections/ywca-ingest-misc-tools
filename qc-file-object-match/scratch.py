import requests
import logging
import sys
import os

fileListFile = "womens-press-files.list"

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

solr_query_template = "http://compass-fedora-prod.fivecolleges.edu:8080/solr/collection1/select?q=mods_identifier_local_s%3A%22{local_id}%22&fl=PID%2Cfgs_label_s%2Cmods_titleInfo_partName_s%2Cmods_titleInfo_title_s&wt=json&indent=true"

with open(fileListFile) as fp:
    for line in fp:
        local_id = os.path.basename(line.strip())
        local_id = local_id.replace(".TIF","").replace(".tif", "")
        logging.debug(local_id)
        query = solr_query_template.format(local_id = local_id)
        logging.debug(query)
        response = requests.get(query)
        logging.debug(response)
        responseData = response.json()
        objects = responseData['response']['docs']

        if len(objects) == 1:
            logging.info("One matching object found %s %s" % (local_id, objects[0]['PID']) )
        if len(objects) < 1:
            logging.error("No matching object found %s" % local_id)
        if len(objects) > 1:
            logging.error("More than one object found %s" % local_id)
