if [ -e test-dirofdirs ]
then
  echo "Deleting old test output small_sample-microdexed/"
  rm -rf test-dirofdirs
fi
cp -a sample-dirofdirs test-dirofdirs
python3 reindex-filenames.py test-dirofdirs
