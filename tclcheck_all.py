#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import tcllib
import sys
from requests.exceptions import RequestException, Timeout

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAM481"
#fc.osvs  = "7.1.1"
fc.mode = fc.MODE_FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE_FULL)
fc.cltp  = 10
#fc.cltp  = 2010

print("List of latest {} firmware by PRD:".format("FULL" if fc.mode == fc.MODE_FULL else "OTA"))

with open("prds.txt", "r") as afile:
    prdx = afile.read()
    prds = list(filter(None, prdx.split("\n")))
for prdline in prds:
    prd, model = prdline.split(" ", 1)
    try:
        fc.reset_session()
        fc.curef = prd
        check_xml = fc.do_check()
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        print("{}: {} {} ({})".format(prd, tv, fhash, model))
    except Timeout as e:
        print("{} failed. (Connection timed out.)".format(prd))
        continue
    except (SystemExit, RequestException) as e:
        print("{} failed. ({})".format(prd, str(e)))
        continue
