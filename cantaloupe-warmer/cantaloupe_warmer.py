""" Request a bunch of images from Cantaloupe in order to grow the cache size
for testing cache expiration settings.
"""

from string import Template
import requests
from requests.utils import quote
import logging

ENVIRONMENT = 'dev'

def getAllLargeImagePids(environment):
    url = "http://compass-fedora-" + environment + ".fivecolleges.edu:8080/solr/collection1/select?q=RELS_EXT_hasModel_uri_s%3Ainfo%5C%3Afedora%5C%2Fislandora%5C%3Asp_large_image_cmodel&fl=PID&wt=json&indent=true&rows=100000"
    response = requests.get(url)
    pids = []
    for solrDoc in response.json()['response']['docs']:
        pids.append(solrDoc['PID'])
    return pids

pids = getAllLargeImagePids(ENVIRONMENT)

print("Querying %s large image objects" % len(pids))

# Make a template for the URL, where $PID represents the incrementing pid
# and $ENVIRONMENT is the environment
urlTemplate = Template("https://compass-$ENVIRONMENT.fivecolleges.edu/iiif/2/$PID~JP2~a27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00https%3A%2F%2Fcompass.fivecolleges.edu%2Fislandora%2Fobject%2F$PID%2Fdatastream%2FJP2%2Fview%3Ftoken%3Da27cf65dff6ca913d5bf4d0516e2280b7446763a185e2c5db8f1f8b24f144a00/full/pct:25/0/default.jpg")

for pid in pids:
    url = urlTemplate.substitute(ENVIRONMENT = ENVIRONMENT, PID = quote(pid))
    logging.debug(url)
    response = requests.get(url)