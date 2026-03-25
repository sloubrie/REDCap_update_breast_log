#!/usr/bin/bash

# Fetch report from REDCap 
echo "Downloading report from REDCap"
API_URL="https://redcap.ucsd.edu/api/"
DATA="token=$REDCAP_TOKEN&content=report&format=csv&report_id=33199"

curl  -H "Content-Type: application/x-www-form-urlencoded" \
      -H "Accept: application/json" \
      -X POST \
      -d $DATA \
      $API_URL \
      >> ./redcap_breast.csv

# Fetch log file from Magickbox computer
echo "Fetching the breast subjects log file"
ssh processing@137.110.129.67 -t "ssh processing@10.198.35.49 -t \"scp /data/hjy004/Breast_subjects.log $USER@137.110.172.113:$PWD\""

# Create updated report for upload to REDCap
echo "Creating updated CSV file for upload to REDCap"
./update_breast_csv.py ./Breast_subjects.log ./redcap_breast.csv 

# Import updated file into REDCap
echo "Uploading CSV file to REDCap"
/home/ccconlin/working/WIL/redcap/venv_redcap/bin/python3 ./post_update.py ./redcap_update.csv

# Delete files with PHI
echo "Cleaning up"
rm ./Breast_subjects.log ./redcap_breast.csv ./redcap_update.csv

echo "Finished"
