#!/bin/bash
python3 ../batch2imi.py sample-batch/ test-output.csv > test-output.log 2>&1
md5 test-output.csv
md5 correct-output/test-output.csv
md5 test-output.log
md5 correct-output/test-output.log
