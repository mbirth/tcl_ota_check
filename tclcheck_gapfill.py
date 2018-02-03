#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import json

import requests
from requests.exceptions import RequestException

import tcllib


# 1. Fetch list of missing OTAs (e.g. from ancient versions to current)
# 2. Query updates from FOTA servers (and store XML)
# (3. Upload will be done manually with upload_logs.py)

fc = tcllib.FotaCheck()
fc.serid = "3531510"
#fc.osvs = "7.1.1"
fc.mode = fc.MODE.OTA
fc.cltp = fc.CLTP.MOBILE

print("Loading list of missing OTAs.")
versions_json = requests.get("https://tclota.birth-online.de/json_otaversions.php").text
versions = json.loads(versions_json)
num_versions = 0
for i in versions:
    num_versions += versions[i]["num_missing"]

print("Got {} devices and a total of {} missing OTAs.".format(len(versions), num_versions))

num_item = 1
for prd, data in versions.items():
    print("{}:".format(prd), end="", flush=True)
    for ver in data["missing_froms"]:
        print(" {}".format(ver), end="", flush=True)
        try:
            fc.reset_session()
            fc.curef = prd
            fc.fv = ver
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            print("✔", end="", flush=True)
        except RequestException as e:
            print("✖", end="", flush=True)
            continue
        num_item += 1
    print("")

tcllib.FotaCheck.write_info_if_dumps_found()
