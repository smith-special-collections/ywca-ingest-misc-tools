#!/bin/bash
python3 ../derivscrudprep.py 2>&1 | sort > output.log
md5sum makecrudfiles.sh-correct makecrudfiles.sh
diff makecrudfiles.sh-correct makecrudfiles.sh
md5sum output.log-correct output.log
diff output.log-correct output.log
