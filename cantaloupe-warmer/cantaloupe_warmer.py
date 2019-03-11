description = """ Request a bunch of images from Cantaloupe in order to grow the cache size
for testing cache expiration settings.
"""

from string import Template
import requests
from requests.utils import quote
from multiprocessing import Pool
import argparse
import logging

def getAllLargeImagePids(environment):
    url = "http://compass-fedora-" + environment + ".fivecolleges.edu:8080/solr/collection1/select?q=(*%3A*+NOT+RELS_EXT_isViewableByRole_literal_s%3A*)+AND+RELS_EXT_hasModel_uri_s%3Ainfo%5C%3Afedora%5C%2Fislandora%5C%3Asp_large_image_cmodel&fl=PID&wt=json&indent=true&rows=100000"
    response = requests.get(url)
    pids = []
    for solrDoc in response.json()['response']['docs']:
        pids.append(solrDoc['PID'])
    return pids

def queryObject(pid):
    # Make a template for the URL, where $PID represents the incrementing pid
    # and $ENVIRONMENT is the environment
    urlTemplate = Template("https://compass-$ENVIRONMENT.fivecolleges.edu/iiif/2/$PID~JP2~a27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00https%3A%2F%2Fcompass.fivecolleges.edu%2Fislandora%2Fobject%2F$PID%2Fdatastream%2FJP2%2Fview%3Ftoken%3Da27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00/full/pct:25/0/default.jpg")
    url = urlTemplate.substitute(ENVIRONMENT = ENVIRONMENT, PID = quote(pid))
    logging.debug(url)
    try:
        requests.get(url)
    except (KeyboardInterrupt, SystemExit):
        logging.debug("Exiting process...")
        return
    # do not return response because we don't want it
    return

if __name__ == '__main__':
    global ENVIRONMENT
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('environment', help="e.g. dev stage or prod")
    parser.add_argument('--debug', action='store_true', help="Print lots of messages")

    args = parser.parse_args()
    ENVIRONMENT = args.environment
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    pids = getAllLargeImagePids(ENVIRONMENT)
    logging.info("Querying %s large image objects" % len(pids))
    # Use multiprocessing to speed up work
    with Pool(processes=10) as pool:
        try:
            pool.map(queryObject, pids)
        except (KeyboardInterrupt, SystemExit):
            logging.info("Exiting program...")
            exit(0)
