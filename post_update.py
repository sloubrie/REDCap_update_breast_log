#!/usr/bin/env python3

import sys
import csv
import os
import requests
import json

path_csv = sys.argv[1]

with open(path_csv, newline='') as csvfile:
     reader = csv.reader(csvfile, delimiter=',')
     headers = next(reader)

     for row in reader:

         record = {
              'mrn': row[0],
              'redcap_event_name': row[1],
              'anonimized_number': row[2],
              'date_of_birth': row[3],
              'mri_scan_date': row[4],
              'mr_facility': row[5],
              'accession_number': row[6],
         }

         data = json.dumps([record])

         fields = {
              'token': os.environ['REDCAP_TOKEN'],
              'content': 'record',
              'format': 'json',
              'type': 'flat',
              'data': data,
         }         

         r = requests.post("https://redcap.ucsd.edu/api/", data=fields)
         print('HTTP Status: ' + str(r.status_code))
         print(r.text)

         if r.status_code == 400:
              break
              



         
