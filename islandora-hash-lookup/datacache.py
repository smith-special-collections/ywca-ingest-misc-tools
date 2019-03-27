import os.path
import pickle
import logging

class DataCache:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data):
        with open(self.filename, 'wb') as fp:
            pickle.dump(data, fp, pickle.HIGHEST_PROTOCOL)

    def load(self):
        if os.path.isfile(self.filename):
            with open(self.filename, 'rb') as fp:
                mydata = pickle.load(fp)
            logging.debug("DataCache found %s" % self.filename)
            return mydata
        else:
            logging.debug("No cache found %s" % self.filename)
            return None
