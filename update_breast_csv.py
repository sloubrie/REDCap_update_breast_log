#!/usr/bin/env python3

import sys
import re
from datetime import datetime
import csv

path_log = sys.argv[1]
path_redcap_csv = sys.argv[2]


# Parse log from Magickbox -------------------------------------------------------
accs = []
mrns = []
dobs = []
scan_dates = []
scanner_nums = []
hash_ids = []

current_entry = ''
with open(path_log) as file:
    for line in file:
        
        line_text = line.rstrip()

        if line_text[0] != '[':
            current_entry = line_text
        else:
            current_entry = current_entry + line_text

        # Accession number
        match_acc = re.search("AccessionNumber \[\w+\]", current_entry)
        if match_acc:
            match_txt = match_acc.group()
            acc = match_txt[17:-1]
        else:
            continue
            
        # MRN
        match_mrn = re.search("MRN \[\d+\]", current_entry)
        if match_mrn:
            match_txt = match_mrn.group()
            mrn = match_txt[5:-1]
        else: 
            continue

        # Date of birth
        match_dob = re.search("DOB \[\d+\]", current_entry)
        if match_dob:
            match_txt = match_dob.group()
            dob = match_txt[5:-1]
            dob = datetime.strptime(dob, "%Y%m%d")
            dob = dob.strftime("%Y-%m-%d")
        else:
            continue

        # Scan date
        match_scan_date = re.search("Exam Date & Time \[\d+[\s\d]*\]", current_entry)
        if match_scan_date:
            match_txt = match_scan_date.group()
            scan_date = match_txt[18:-8]
            scan_date = scan_date.replace(" ", "0")
            scan_date = datetime.strptime(scan_date, "%Y%m%d")
            scan_date = scan_date.strftime("%Y-%m-%d")
        else:
            continue

        # Scanner
        match_scanner = re.search("Scanner used \[\w+\]", current_entry)
        if match_scanner:
            match_txt = match_scanner.group()
            scanner = match_txt[14:-1]
        else:
            continue

        if scanner == "MR0OW4":
            scanner_num = "1"
        elif "KOP" in scanner:
            scanner_num = "2"
        elif "MR1MR1" in scanner:
            scanner_num = "3"
        else:
            scanner_num = "4"

        # Hash
        match_hash = re.search("ID String \[\w+\]", current_entry)
        if match_hash:
            match_txt = match_hash.group()
            hash_id = match_txt[11:-1]
        else:
            continue

        if acc not in accs:
            accs.append(acc)
            mrns.append(mrn)
            dobs.append(dob)
            scan_dates.append(scan_date)
            scanner_nums.append(scanner_num)
            hash_ids.append(hash_id)


# Parse CSV from REDCap -------------------------------------------------------
rc_accs = []
rc_mrns = []
rc_dobs = []
rc_scan_dates = []
rc_scanner_nums = []
rc_hash_ids = []
rc_event_name = []

with open(path_redcap_csv, newline='') as csvfile:
     reader = csv.reader(csvfile, delimiter=',')
     for row in reader:
         rc_accs.append(row[6])
         rc_mrns.append(row[0])
         rc_dobs.append(row[3])
         rc_scan_dates.append(row[4])
         rc_scanner_nums.append(row[5])
         rc_hash_ids.append(row[2])
         rc_event_name.append(row[1])


# Create new, updated CSV for upload to REDCap --------------------------------
for i in range(len(mrns)):

    if mrns[i] not in rc_mrns:
        print(mrns[i] + " is a new patient, adding to REDCap file")
        rc_accs.append(accs[i])
        rc_mrns.append(mrns[i])
        rc_dobs.append(dobs[i])
        rc_scan_dates.append(scan_dates[i])
        rc_scanner_nums.append(scanner_nums[i])
        rc_hash_ids.append(hash_ids[i])
        rc_event_name.append("mri_1_arm_1")

    else:
        matches = [j for j in range(len(rc_mrns)) if rc_mrns[j]==mrns[i]]
        matched_accs = [rc_accs[j] for j in matches]
        if accs[i] not in matched_accs:
            print(mrns[i] + " is a returning patient with a new scan (Acc #: " + accs[i] +  "), adding to REDCap file")
            highest_match = max(matches)
            rc_accs = rc_accs[:highest_match+1] + [accs[i]] + rc_accs[highest_match+1:]
            rc_mrns = rc_mrns[:highest_match+1] + [mrns[i]] + rc_mrns[highest_match+1:]
            rc_dobs = rc_dobs[:highest_match+1] + [''] + rc_dobs[highest_match+1:]
            rc_scan_dates = rc_scan_dates[:highest_match+1] + [scan_dates[i]] + rc_scan_dates[highest_match+1:]
            rc_scanner_nums = rc_scanner_nums[:highest_match+1] + [scanner_nums[i]] + rc_scanner_nums[highest_match+1:]
            rc_hash_ids = rc_hash_ids[:highest_match+1] + [''] + rc_hash_ids[highest_match+1:]
            rc_event_name = rc_event_name[:highest_match+1] + ["mri_" + str(len(matches)+1) + "_arm_1"] + rc_event_name[highest_match+1:]


with open('redcap_update.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    for i in range(len(rc_mrns)):
        writer.writerow([rc_mrns[i], rc_event_name[i], rc_hash_ids[i], rc_dobs[i], rc_scan_dates[i], rc_scanner_nums[i], rc_accs[i]])

