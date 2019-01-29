#!/bin/bash
python3 ../batch2imi.py sample-batch/ test-output smith:test --remote-path /ingest/dir/ > test-output.log 2>&1
md5sum test-output.csv
md5sum correct-output/test-output.csv
md5sum test-output.log
md5sum correct-output/test-output.log
