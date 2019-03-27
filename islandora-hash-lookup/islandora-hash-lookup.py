"""
[x] Get all hashes via downloading TECHMD datastreams and put them in a datastructure
[x] Also, cache them
[x] Or if there's a cache and it's not expired use that
[] Search data structure for the item
[] Print out its PID

Architectual Decisions
If Solr had the md5s I would use that but it doesnn't. Apparently it's possible to index that data via a gsearch xslt. However, the human effort to set that up and reindex is greater than the effort to just scrape the data from Fedora and search within memory locally.

"""
import sys
import logging
import os.path
import pickle
from bs4 import BeautifulSoup
import requests_cache

from solr import Solr
from fedora import Fedora

SMALL_TEST_SET = True

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("requests").setLevel(logging.WARNING)

# Set up a local cache of http requests to Solr and Fedora
requests_cache.install_cache('requests_cache')

# Set up a bulk data cache using Python pickles for storing data sets
# for later use. This is needed in addition to the http cache because
# when working with a million+ datapoints even that doesn't 
# improve performance enough to provide instantaneous lookups.
class Cache:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data):
        with open(self.filename, 'wb') as fp:
            pickle.dump(data, fp, pickle.HIGHEST_PROTOCOL)

    def load(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as fp:
                mydata = pickle.load(fp)
            logging.debug("Cache found %s" % self.filename)
            return mydata
        else:
            logging.debug("No cache found %s" % self.filename)
            return None

def getAllObjectPids():

    # Check cache first
    cache = Cache('allpids.cache')
    allpids = cache.load()
    if allpids:
        return allpids
    else:
        # If no cache do this
        solr = Solr()
        solr.loadConfig('solr.cfg','prod')
        queryParams = {
            'q':'*:*',
            'fl': 'PID',
        }
        response = solr.query(queryParams)
        allpids = list(map(lambda x: x['PID'], response))
        cache.save(allpids)
        return allpids

# Make getAllObjectPids() return a much smaller list if in test mode
if SMALL_TEST_SET:
    logging.warning("SMALL_TEST_SET = True")
    getAllObjectPids = lambda: ["smith:%s" % i for i in range(169270, 169449) if True]

def getObjectMd5(fedora, pid):
    """Parses the TECHMD datastream file for the <md5checksum> tag
    """

    try:
        namespace = pid.split(':')[0]
        pidnumber = pid.split(':')[1]
        datastreamContents = fedora.getDatastream(namespace, pidnumber, 'TECHMD')
        soup = BeautifulSoup(datastreamContents, features="html.parser")
        md5sum = soup.md5checksum.contents[0]
        return md5sum
    except Exception as e:
        logging.error("Could not get md5sum for %s %s" % (pid, e))
        return None

def getAllObjectMd5s(pids):
    """Suck down all checksums from Fedora
    Returns a dictionary of pids and md5 sums
    """

    # Check cache first
    cache = Cache('remotemd5s.cache')
    allmd5s = cache.load()
    if allmd5s:
        return allmd5s
    else:
        allmd5s = {}
        fedora = Fedora()
        fedora.loadConfig('fedora.cfg', 'prod')
        
        for pid in pids:
            md5sum = getObjectMd5(fedora, pid)
            allmd5s[pid] = md5sum
            logging.debug("%s %s" % (md5sum, pid))
        
        cache.save(allmd5s)
    
    return allmd5s

if __name__ == "__main__":
    "Main function"

    pids = getAllObjectPids()
    remoteMd5s = getAllObjectMd5s(pids)
    logging.debug("remoteMd5s memory footprint: %s" % sys.getsizeof(remoteMd5s))
    import pdb; pdb.set_trace()

    # for inputLine in fileinput.input():
    #     _inputLine = inputLine.strip() # remove trailing newline
    #     print(_inputLine)
