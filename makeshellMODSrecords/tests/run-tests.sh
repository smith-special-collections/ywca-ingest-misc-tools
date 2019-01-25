#!/bin/bash
if [ -e sample-batch-batched ]
then
  echo "Deleting old test output sample-batch-batched /"
  rm -rf sample-batch-batched
fi

python3 ../makeshellMODSrecords.py sample-batch/ 'smith*' > test-output.log 2>&1
md5 test-output.log
md5 correct-output/test-output.log 
echo "diff -r correct-output/sample-batch-batched sample-batch-batched"
diff -r correct-output/sample-batch-batched sample-batch-batched
