# 'dir2localid.list' is made with the following command:
# find /mnt/ingest/smith/1k-photos-test-all-files -name MODS.xml | xargs grep local | sed -e 's/<[^>]*>//g' > dir2localid.list
#
# 'pid2localid.json' is made with the following command:
# curl "http://compass-fedora-stage.fivecolleges.edu:8080/solr/collection1/select?q=fgs_createdDate_dt%3A+%5B2019-02-03T20%3A23%3A00.000Z+TO+2019-02-03T21%3A11%3A00.000Z%5D+AND+PID%3Atest%5C%3A*&wt=json&indent=true&rows=100000&fl=PID%2Cfgs_label_s%2CRELS_EXT_hasModel_uri_s%2Cfgs_createdDate_dt%2Cfgs_lastModifiedDate_dt%2Cfgs_ownerId_s%2Cmods_identifier_local_s" > pid2localid.json
#
# Then use islandora CRUD:
# /mnt/ingest/smith/photographs-test-lc/crud_files
# --no_derivs
# 

import json
from string import Template
import logging

fileListFile = "dir2localid.list"
solrOutput = "pid2localid.json"
outputDir = 'crud_files'
commandProgramOutput = 'makecrudfiles.sh'

datastreams = {
    'TN': 'TN.jpg',
    'JPG': 'JPG.jpg',
    'LARGE_JPG': 'LARGE_JPG.jpg',
    'JP2': 'JP2.jp2',
    'OCR': 'OCR.txt',
}

# Make a mapping between local ID and directory of datastreams
def makeDirMapping(fileListFile):
    mapping = {}
    with open(fileListFile) as fp:
        for line in fp:
            line = line.strip()
            mysplit = line.split(':    ')
            local_id = mysplit[1]
            path = mysplit[0].replace('MODS.xml', '')
            mapping[local_id] = path
    return mapping

def makePidMapping(solrOutput):
    with open(solrOutput) as fp:
        myJson = json.load(fp)
    return myJson['response']['docs']

def makePid2DirMapping(dirMapping, pidMapping):
    pid2DirMapping = {}
    for record in pidMapping:
        pid = record['PID']
        try:
            localId = record['mods_identifier_local_s']
        except KeyError as e:
            logging.error("%s does not have a key called 'mods_identifier_local_s' %s" % (pid, record))
        try:
            dir = dirMapping[localId]
        except KeyError as e:
            logging.error("Could not match %s" % e)
        else:
            # print('%s %s datastreams located in %s' % (localId, pid, dir))
            pid2DirMapping[pid] = { 'dir': dir, 'local_id': localId}
    return pid2DirMapping

def makeCommandProgram(pid2DirMapping):
    # Keep a list of the commands that will be run
    commandProgram = []

    # Make directories for each datastream type (it's the way crud needs it)
    for datastreamName, datastreamFilename in datastreams.items():
        commandTemplate = Template("mkdir $outputDir/$datastreamName")
        command = commandTemplate.substitute(
            outputDir=outputDir,
            datastreamName=datastreamName
        )
        commandProgram.append(command)

    # Copy files into an output dir with crud friendly filename format
    # keep each type in its own directory
    for pid,values in pid2DirMapping.items():        
        commandTemplate = Template("cp $srcDir/$originalFilename $outputDir/$datastreamName/$crudFilename")

        # Go through the various datastream types
        for datastreamName, datastreamFilename  in datastreams.items():
            srcDir = values['dir']
            originalFilename = datastreamFilename
            crudFilename = pid.replace(':', '_') + '_' + originalFilename
            command = commandTemplate.substitute(
                srcDir=srcDir,
                originalFilename=originalFilename,
                outputDir=outputDir,
                crudFilename=crudFilename,
                datastreamName=datastreamName
            )
            commandProgram.append(command)
    
    return commandProgram

dirMapping = makeDirMapping(fileListFile)
pidMapping = makePidMapping(solrOutput)

# Do the mapping, and generate the commands
pid2DirMapping = makePid2DirMapping(dirMapping, pidMapping)
commandProgram = makeCommandProgram(pid2DirMapping)

with open(commandProgramOutput, 'w') as outfile:
    for line in commandProgram:
        outfile.write(line + '\n')
