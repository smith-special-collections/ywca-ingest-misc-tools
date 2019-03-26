import requests
import math
import configparser
import logging

class Solr(object):
    """Handle Solr queries"""
    
    def __init__(self):
        self.session = requests.Session()

    def loadConfig(self, configFile, configSection):
        """Load connection details from a config file
        """

        self.config = None

        try:
            config = configparser.ConfigParser()
            config.read_file(open(configFile), source=configFile)
            configData = config[configSection]
        except FileNotFoundError:
            print("Can't find a config file called %s" % configFile)
            exit(1)
        except KeyError as e:
            print("Config file %s doesn't contain that section %s" % (configFile, e))
            exit(1)

        myConfig = {}

        try:
            myConfig['url'] = configData['url']
        except KeyError as e:
            print("Config file section '%s' doesn't contain required property %s" % (configSection, e))
            exit(1)

        self.config = myConfig

    def query(self, params):
        PAGE_SIZE = 10000
        params['wt'] = 'json'
        params['rows'] = PAGE_SIZE

        def getNumPages():
            _response = self.session.get(self.config['url'], params=params)
            logging.debug("Raw response initial: %s" % _response.content)
            httpCode = _response.status_code
            if httpCode == 400:
                logging.error("Bad request")
                return None
            else:
                numFound = _response.json()['response']['numFound']
                numPages = math.ceil(numFound/PAGE_SIZE)
                return numPages

        numPages = getNumPages()

        allRecords = []
        # Now page through the results
        logging.debug("Page size %s, numPages %s" % (PAGE_SIZE, numPages))
        for pageNum in range(0, numPages):
            logging.debug(pageNum)
            params['start'] = pageNum * PAGE_SIZE
            _response = self.session.get(self.config['url'], params=params)
            logging.debug("Raw response: %s" % _response.content)
            allRecords.extend(_response.json()['response']['docs'])
        
        return allRecords
        
