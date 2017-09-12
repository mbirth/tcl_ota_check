#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import tcllib
from requests.exceptions import RequestException, Timeout

ANSI_UP_DEL = u"\u001b[F\u001b[K"

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

while len(prds) > 0:
    prd, model = prds[0].split(" ", 1)
    try:
        fc.reset_session()
        fc.curef = prd
        check_xml = fc.do_check()
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        print("{}: {} {} ({})".format(prd, tv, fhash, model))
        prds.pop(0)
    except Timeout as e:
        print("{} failed. (Connection timed out.)".format(prd))
        print(ANSI_UP_DEL, end="")
        continue
    except (SystemExit, RequestException) as e:
        print("{} failed. ({})".format(prd, str(e)))
        if e.response.status_code in [204, 404]:
            # No update available or invalid request - remove from queue
            prds.pop(0)
        else:
            print(ANSI_UP_DEL, end="")
        continue
