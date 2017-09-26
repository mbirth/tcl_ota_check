#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import collections
import tcllib
from requests.exceptions import RequestException, Timeout

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE_FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE_FULL)
#fc.cltp  = 10
fc.cltp  = 2010

print("Valid PRDs not already in database:")

with open("prds.txt", "r") as afile:
    prddict = collections.defaultdict(list)
    prda = afile.readlines()
    prds = [x.split(" ")[0].replace("PRD-", "").split("-") for x in prda]
    prdx = list({x[0]: x[1]} for x in prds)
    for prdc in prdx:
        for key, value in prdc.items():
            prddict[key].append(value)

for center in prddict.keys():
    tails = [int(i) for i in prddict[center]]
    for j in range(0, 1000):
        if j not in tails:
            curef = "PRD-{}-{}".format(center, str(j).rjust(3, "0"))
            try:
                fc.reset_session()
                fc.curef = curef
                check_xml = fc.do_check(https=False)
                curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
                txt_tv = tv
                print("{}: {} {}".format(curef, txt_tv, fhash))
            except (SystemExit, RequestException, Timeout) as e:
                continue
