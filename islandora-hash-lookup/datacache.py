import os.path
import pickle
import logging
from datetime import datetime, timedelta

BACKUP_MIN_DELAY = timedelta(minutes=6)

class DataCache:
    """
    Two modes: lookup table, and bulk data
    
    Also: automatic backup of data to cache file. But you must do a request
    after the specified minimum delay for it to happen.
    
    Lookup table mode:
    >>> import logging, sys
    >>> logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    >>> 
    >>> from datacache import DataCache
    >>> mycache = DataCache(".mytest.cache", get_callback = lambda x: x * x)
    DEBUG:root:No cache found .mytest.cache
    >>> mycache.get(100)
    DEBUG:root:Key not found in cache table. Calling callback.
    DEBUG:root:Saving value to cache table
    10000
    >>> 
    >>> mycache.get(100)
    DEBUG:root:Value found in cache table
    10000
    >>> 
    >>> mycache.get(10)
    DEBUG:root:Key not found in cache table. Calling callback.
    DEBUG:root:Saving value to cache table
    100
    >>> 
    >>> mycache.get(10)
    DEBUG:root:Value found in cache table
    100
    >>> 
    >>> mycache.get(100)
    DEBUG:root:Value found in cache table
    10000
    >>> 
    >>> mycache.save()
    >>> 
    >>> mycache = DataCache(".mytest.cache", get_callback = lambda x: x * x)
    DEBUG:root:DataCache found .mytest.cache
    >>> mycache.get(100)
    DEBUG:root:Value found in cache table
    10000
    >>> 
    >>> mycache.get(10)
    DEBUG:root:Value found in cache table
    100
    >>> 
    >>> mycache.get(3.141)
    DEBUG:root:Key not found in cache table. Calling callback.
    DEBUG:root:Saving value to cache table
    9.865881
    >>> 
    """
    
    def __init__(self, _filename, get_callback=None, backup_min_delay=BACKUP_MIN_DELAY):
        self._filename = _filename
        self._dataTable = None
        self.get_callback = get_callback
        self.last_backup = datetime.now()
        self.backup_min_delay = backup_min_delay

        if os.path.isfile(self._filename):
            with open(self._filename, 'rb') as fp:
                mydata = pickle.load(fp)
            logging.debug("DataCache found %s" % self._filename)
            self._dataTable = mydata
        else:
            logging.debug("No cache found %s" % self._filename)
            self._dataTable = {}

    def save(self, bulk_data=None):
        if bulk_data:
            self._dataTable = bulk_data
        
        with open(self._filename, 'wb') as fp:
            pickle.dump(self._dataTable, fp, pickle.HIGHEST_PROTOCOL)

    def get(self, key):
        try:
            value = self._dataTable[key]
            logging.debug("Value found in cache table")
            return value
        except KeyError:
            logging.debug("Key not found in cache table. Calling callback.")
            result = self.get_callback(key)
            logging.debug("Saving value to cache table")
            self._dataTable[key] = result
            if datetime.now() - self.last_backup > self.backup_min_delay:
                logging.debug("Saving cache table to file")
                self.save()
                self.last_backup = datetime.now()
            return result

    def getBulkData(self):
        return self._dataTable
