derivscrudprep
-------------
Use this tool to prepare files from a batch ingest to be post-facto ingested by Islandora CRUD after the main OBJs have been ingested using Islandora Compound Batch.

Copies files from a batch folder into individual directories, one for each datastream. Renames them them to match Islandora CRUD naming convention, e.g. `smith_30874_JP2.jp2`.

Does the assignment of the PID via matching between two data files:

'dir2localid.list' is made with the following command:
```
find /mnt/ingest/smith/1k-photos-test-all-files -name MODS.xml | xargs grep local | sed -e 's/<[^>]*>//g' > dir2localid.list
```

'pid2localid.json' is made with the following command:
```
curl "http://compass-fedora-stage.fivecolleges.edu:8080/solr/collection1/select?q=fgs_createdDate_dt%3A+%5B2019-02-03T20%3A23%3A00.000Z+TO+2019-02-03T21%3A11%3A00.000Z%5D+AND+PID%3Atest%5C%3A*&wt=json&indent=true&rows=100000&fl=PID%2Cfgs_label_s%2CRELS_EXT_hasModel_uri_s%2Cfgs_createdDate_dt%2Cfgs_lastModifiedDate_dt%2Cfgs_ownerId_s%2Cmods_identifier_local_s" > pid2localid.json
```

Then **derivscrudprep.py** is used to generate a bash script full of the commands to make the crud ingest directories `makecrudfiles.sh`. That script is then run on the server.

Note that the relevant input and output files are located in code:
```
fileListFile = "dir2localid.list"
solrOutput = "pid2localid.json"
outputDir = 'crud_files'
commandProgramOutput = 'makecrudfiles.sh'
```
