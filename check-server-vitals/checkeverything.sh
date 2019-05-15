#!/bin/bash
echo "### WEBHEAD ###"
ssh islandora@compass.fivecolleges.edu "df -h"
echo "-- /tmp dir"
ssh islandora@compass.fivecolleges.edu "sudo du -hs /tmp"
echo "-- Drupal files"
ssh islandora@compass.fivecolleges.edu "du -hs /var/www/html/sites/default/files"
ssh islandora@compass.fivecolleges.edu "ls -1 /var/www/html/sites/default/files | wc -l"
echo "-- Num records in Batch Queue table"
ssh islandora@compass.fivecolleges.edu "./get_num_rcrds_in_batch_queue_table.sh"
echo "### FEDORA MACHINE ###"
ssh islandora@compass.fivecolleges.edu 'ssh islandora@compass-fedora-prod.fivecolleges.edu "df -h"'
echo "-- Cantaloupe cache"
ssh islandora@compass.fivecolleges.edu 'ssh islandora@compass-fedora-prod.fivecolleges.edu "du -hs /var/cache/cantaloupe"'
echo "--"
echo "### DRIFTWOOD ###"
ssh driftwood "df -h"
