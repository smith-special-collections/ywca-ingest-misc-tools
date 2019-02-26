description = """Create a bash script called makecrudfiles.sh which, when run,
will create files appropriately named and organized for Islandora CRUD.
It copies the files from a batch directory into individual directories for each
datastream and renames those files to include the target PID. Requires
\"dir2localid.list\" and \"pid2localid.json\" to exist in the current
directory. Read the README for more details."""

import json
from string import Template
import logging
import argparse

argparser = argparse.ArgumentParser(description=description)
argparser.add_argument('OUTPUTDIR', help="Full path of the location in which crud files should be copied to. e.g. /mnt/ingest/smith/1k-photos-test-all-files/crud_files")
cliargs = argparser.parse_args()

fileListFile = "dir2localid.list"
solrOutput = "pid2localid.json"
outputDir = cliargs.OUTPUTDIR
commandProgramOutput = 'makecrudfiles.sh'
drushCommandsOutput = 'drushcommands.sh'

datastreams = {
    'JP2': {'filename': 'JP2.jp2', 'mimetype': 'image/jp2', 'label':'JPEG 2000'},
    'TN': {'filename': 'TN.jpg', 'mimetype': 'image/jpeg', 'label':'Thumbnail'},
    'JPG': {'filename': 'JPG.jpg', 'mimetype': 'image/jpeg', 'label':'Medium sized JPEG'},
    'OCR': {'filename': 'OCR.txt', 'mimetype': 'text/plain', 'label':'OCR Datastream'},
    'LARGE_JPG': {'filename': 'LARGE_JPG.jpg', 'mimetype': 'image/jpeg', 'label':'Large JPG'},
    'TECHMD': {'filename': 'TECHMD.xml', 'mimetype': 'application/xml', 'label':'TECHMD'},
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
            logging.error("%s does not have a key called 'mods_identifier_local_s'" % pid)
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
    for datastreamName, datastreamData in datastreams.items():
        commandTemplate = Template("mkdir $outputDir/$datastreamName")
        command = commandTemplate.substitute(
            outputDir=outputDir,
            datastreamName=datastreamName
        )
        commandProgram.append(command)

    # Copy files into an output dir with crud friendly filename format
    # keep each type in its own directory
    for pid,values in pid2DirMapping.items():        
        commandTemplate = Template("mv $srcDir/$originalFilename $outputDir/$datastreamName/$crudFilename")

        # Go through the various datastream types
        for datastreamName, datastreamData  in datastreams.items():
            srcDir = values['dir']
            originalFilename = datastreamData['filename']
            crudFilename = pid.replace(':', '_') + '_' + originalFilename
            command = commandTemplate.substitute(
                srcDir=srcDir,
                originalFilename=originalFilename,
                outputDir=outputDir,
                crudFilename=crudFilename,
                datastreamName=datastreamName
            )
            commandProgram.append(command)
        commandProgram.sort() # make output consistent for automated tests
    return commandProgram

def makeDrushCommands(datastreams, directory):
    commandTemplate = Template("date && time -p drush islandora_datastream_crud_push_datastreams --user=1 --datastreams_mimetype=\"$mimetype\" --datastreams_source_directory=\"$directory/$datastream\" --datastreams_crud_log=$directory/crud-`date +%s`.log -y --datastreams_label=\"$label\" > $directory/$datastream-`date +%s`.log 2>&1 && date")
    commandProgram = []
    for datastream, datastreamData in datastreams.items():
        command = commandTemplate.substitute(
            datastream=datastream,
            mimetype=datastreamData['mimetype'],
            directory=directory,
            label=datastreamData['label'],
        )
        commandProgram.append(command)

    commandProgram.sort() # make output consistent for automated tests
    return commandProgram

def writeCommandOutput(commandProgram, commandProgramOutput):
    with open(commandProgramOutput, 'w') as outfile:
        for line in commandProgram:
            outfile.write(line + '\n')

if __name__ == '__main__':
    dirMapping = makeDirMapping(fileListFile)
    pidMapping = makePidMapping(solrOutput)

    # Do the mapping, and generate the commands
    pid2DirMapping = makePid2DirMapping(dirMapping, pidMapping)
    commandProgram = makeCommandProgram(pid2DirMapping)
    writeCommandOutput(commandProgram, commandProgramOutput)

    # Also generate a handy drush commands file
    drushProgram = makeDrushCommands(datastreams, outputDir)
    writeCommandOutput(drushProgram, drushCommandsOutput)
