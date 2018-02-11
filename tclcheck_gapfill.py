#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Query existence of missing OTAs."""

import json
import requests

from tcllib import ansi
from tcllib.devices import MobileDevice
from tcllib.dumpmgr import write_info_if_dumps_found
from tcllib.requests import RequestRunner, CheckRequest, ServerVoteSelector


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
            print("✔", end="", flush=True)
            num_item += 1
        else:
            print("✖", end="", flush=True)
    print("")

write_info_if_dumps_found()
