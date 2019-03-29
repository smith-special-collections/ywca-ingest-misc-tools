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
    # Take from list in 1k chunks and process each one at a time
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

def writeShellModsFile(outputDir, pid, localid):
    """ Write shell record MODS file with a file name compatable with
    Islandora Datastream CRUD.
    
    >>> writeShellModsFile('mods_output', 'smith:999', 'local_id_for_realz-31415926')
    >>>
    >>> with open('mods_output/smith_999_MODS.xml', 'r') as fp:
    ...     print(fp.read(), end='')
    ...
    <?xml version="1.0" encoding="UTF-8"?>
    <mods xmlns="http://www.loc.gov/mods/v3" xmlns:mods="http://www.loc.gov/mods/v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink">
        <titleInfo>
            <title>local_id_for_realz-31415926</title>
        </titleInfo>
        <identifier type="local">local_id_for_realz-31415926</identifier>
    </mods>
    >>>
    """

    # MODS template for page level metadata (just ID for linking)
    with open('modstemplate.xml', 'r') as fp:
        pageModsTemplate = fp.read()

    modsOutput = pageModsTemplate.format(identifier=localid)
    filepathname = outputDir + '/' + pid.replace(':', '_') + '_MODS.xml'
    logging.info("Generate %s" % filepathname)
    with open(filepathname, 'w') as modsFile:
        modsFile.write(modsOutput)

def filepathnameToLocalId(filepathname):
    localId = filepathname.split('/')[-1].split('.')[0]
    return localId

def exportMods(db, outputDir, pid):
    selectCommand = \
    """select md5s_remote.md5, md5s_remote.pid, md5s_local.fullpath
      from md5s_remote join md5s_local
      where md5s_remote.md5 = md5s_local.md5
      and md5s_remote.pid = '{pid}';
    """
    
    _selectCommand = selectCommand.format(pid = pid)
    db.cursor.execute(_selectCommand)
    row = db.cursor.fetchone()
    try:
        pid = row[1]
        _localid = row[2]
    except TypeError as e:
        logging.error("Could not find local id for %s from database: %s" % (pid, e))
        return
    else:
        localid = filepathnameToLocalId(_localid)
        writeShellModsFile(outputDir, pid, localid)

def exportMods_multi(db, outputDir, pidsfile):
    with open(pidsfile, 'r') as fp:
        for line in fp:
            exportMods(db, outputDir, line.strip())

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    parser = argparse.ArgumentParser()
    parser.add_argument("COMMAND", choices=['get-pids', 'fetch-remote-md5s', 'export-mods', 'export-mods-multi', 'debug-shell'])
    parser.add_argument("--data-file", default='data.sqlite', help="Name of file to read and write data")
    parser.add_argument("--output-dir", default='mods_output', help="Name of dir to dump mods.xml files to")
    parser.add_argument("--pid", help="pid of object to export MODS file for")
    parser.add_argument("--pidsfile", help="File containing a list of pids to export MODS files for, one pid per line")
    args = parser.parse_args()
    
    db = Database(args.data_file)
    outputDir = args.output_dir
    pid = args.pid
    pidsfile = args.pidsfile
    
    db.initializeDb()
    if args.COMMAND == 'get-pids':
        loadAllObjectPids(db)
    elif args.COMMAND == 'fetch-remote-md5s':
        loadAllObjectMd5s(db)
    elif args.COMMAND == 'export-mods':
        exportMods(db, outputDir, pid)
    elif args.COMMAND == 'export-mods-multi':
        exportMods_multi(db, outputDir, pidsfile)
    elif args.COMMAND == 'debug-shell':
        pdb.set_trace()

    db.connection.close()
