#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Query existence of missing OTAs."""

import json
import sys

import requests

from tcllib import argparser
from tcllib.devices import MobileDevice
from tcllib.dumpmgr import write_info_if_dumps_found
from tcllib.requests import CheckRequest, RequestRunner, ServerVoteSelector


dpdesc = """
    Queries the database server for known versions and tries to find OTA files not yet in the database.
"""
dp = argparser.DefaultParser(__file__, dpdesc)
args = dp.parse_args(sys.argv[1:])
del args


# 1. Fetch list of missing OTAs (e.g. from ancient versions to current)
# 2. Query updates from FOTA servers (and store XML)
# (3. Upload will be done manually with upload_logs.py)


print("Loading list of missing OTAs.")
versions_json = requests.get("https://tclota.birth-online.de/json_otaversions.php").text
versions = json.loads(versions_json)
num_versions = 0
for i in versions:
    num_versions += versions[i]["num_missing"]

print("Got {} devices and a total of {} missing OTAs.".format(len(versions), num_versions))

dev = MobileDevice()

runner = RequestRunner(ServerVoteSelector())
runner.max_tries = 20

num_item = 1
for prd, data in versions.items():
    print("{}:".format(prd), end="", flush=True)
    for ver in data["missing_froms"]:
        print(" {}".format(ver), end="", flush=True)
        dev.curef = prd
        dev.fwver = ver
        chk = CheckRequest(dev)
        runner.run(chk)
        if chk.success:
            if chk.result.tvver == data["latest_ota"]:
                print("✔", end="", flush=True)
                num_item += 1
            elif chk.result.tvver in data["update_map"] and ver in data["update_map"][chk.result.tvver]:
                # Delete dump as we already know the information
                chk.result.delete_dump()
                print("%", end="", flush=True)
            else:
                print("~", end="", flush=True)
        else:
            print("✖", end="", flush=True)
    print("")

write_info_if_dumps_found()
