import sqlite3
import logging
import sys
import argparse
import pdb

from solr import Solr
from fedora import Fedora

"""

Database
table: md5s_remote
fields: pid, md5, fetched

"""

class Database():
    def __init__(self, sqlite_file):
        self.connection = sqlite3.connect(sqlite_file)
        self.cursor = self.connection.cursor()

    def initializeDb(self):
        try:
            self.cursor.execute("CREATE TABLE md5s_remote (pid PRIMARY KEY, md5, fetched INTEGER)")
            self.connection.commit()
        except sqlite3.OperationalError:
            logging.debug("Database table already exists, skipping initialization")

def loadAllObjectPids(db):
    solr = Solr()
    solr.loadConfig('solr.cfg','prod')
    queryParams = {
        'q':'*:*',
        'fl': 'PID',
    }
#    Test small sample
    # queryParams = {
    #     'q':'RELS_EXT_isConstituentOf_uri_s:info\:fedora\/mtholyoke\:25060',
    #     'fl': 'PID',
    # }

    response = solr.query(queryParams)
    allpids = list(map(lambda x: x['PID'], response))
    for pid in allpids:
        try:
            db.cursor.execute("INSERT INTO md5s_remote VALUES ('%s', NULL, 0)" % pid)
        except sqlite3.IntegrityError as e:
            logging.warning(str(e) + ' ' + pid)
    db.connection.commit()

def loadAllObjectMd5s(db):
    """Suck down all checksums from Fedora
    Check database for unretrieved md5s
    Those that have fetched False are queried from Fedora
    Parses the TECHMD file for the md5 tag
    """

    logging.debug("loadAllObjectMd5s")
    fedora = Fedora()
    fedora.loadConfig('fedora.cfg', 'prod')

    # What entries in the local data store don't have md5s yet?
    # Examples: is this a second attempt? Are we actually done?
    # Take from list in 10k chunks and process each one at a time
    # This avoids doing two queries at the same time. Also leaves
    # opens the possibility of multiprocessing.

    batchSize = 1000
    while True:
        _selectCommand = "SELECT pid FROM md5s_remote WHERE fetched == 0 LIMIT %s" % (batchSize)
        logging.debug(_selectCommand)
        db.cursor.execute(_selectCommand)
        rows = db.cursor.fetchmany(batchSize)
        if not rows:
            logging.info("All items fetched")
            break
        batchPids = list(map(lambda x: x[0], rows))
        batchMatches = list(map(lambda x: {'pid': x, 'md5sum': fedora.getObjectMd5(x)}, batchPids))
        for match in batchMatches:
            _updateCommand = "UPDATE md5s_remote set md5='%s', fetched=1 WHERE pid == '%s'" % (match['md5sum'], match['pid'])
            logging.debug(_updateCommand)
            db.cursor.execute(_updateCommand)
        db.connection.commit()
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("COMMAND", choices=['get-pids', 'fetch-remote-md5s'])
    parser.add_argument("--data-file", default='data.sqlite', help="Name of file to read and write data")
    args = parser.parse_args()
    
    db = Database(args.data_file)
    
    db.initializeDb()
    if args.COMMAND == 'get-pids':
        loadAllObjectPids(db)
    if args.COMMAND == 'fetch-remote-md5s':
        loadAllObjectMd5s(db)

    db.connection.close()
