import requests
import string
import configparser
import logging

class Fedora:
    def __init__(self):
        # Start a requests session for better formance (measured 1.77x faster)
        self.session = requests.Session()

    def getDatastream(self, namespace, pidnumber, datastream):
        "Fetch a datastream and return its contents"

        logging.debug("Fedora.getDatastream")
        
        def makeFedoraURL(namespace, pidnumber, datastreamName):
            urlTemplate = string.Template("https://$environment:$port/fedora/objects/$namespace:$pidnumber/datastreams/$datastream/content")
            url = urlTemplate.substitute(
                environment = self.config['ENVIRONMENT'],
                port = self.config['FEDORA_PORT'],
                namespace = namespace,
                pidnumber = pidnumber,
                datastream = datastreamName,
            )
            return url

        url = makeFedoraURL(namespace, pidnumber, datastream)
        username = self.config['FEDORA_USER']
        password = self.config['FEDORA_PASS']
        httpResponse = self.session.get(url, auth=(username, password))
        if httpResponse.status_code == 200:
            return httpResponse.content
        else:
            logging.error("Failed to fetch remote datastream for %s because %s" % (url, httpResponse.status_code))
            return None

    def loadConfig(self, configFile, configSection):
        """Load connection details from a config file

        >>> fedora = Fedora()
        >>> fedora.loadConfig('example-fedora.cfg', 'prod')
        >>> fedora.config['FEDORA_USER']
        'fedora_acct'
        >>> fedora.config['FEDORA_PASS']
        'supersecret'
        >>> fedora.config['ENVIRONMENT']
        'fedora-prod.example.edu'
        >>> fedora.config['FEDORA_PORT']
        '8443'
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

        fedoraConfig = {}

        try:
            fedoraConfig['ENVIRONMENT'] = configData['hostname']
            fedoraConfig['FEDORA_PORT'] = configData['port']
            fedoraConfig['FEDORA_USER'] = configData['username']
            fedoraConfig['FEDORA_PASS'] = configData['password']
        except KeyError as e:
            print("Config file section '%s' doesn't contain required property %s" % (configSection, e))
            exit(1)

        self.config = fedoraConfig
