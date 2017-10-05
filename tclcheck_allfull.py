#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import tcllib
from requests.exceptions import RequestException, Timeout

tcllib.make_escapes_work()

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE_FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE_FULL)
#fc.cltp  = 10
fc.cltp  = 2010
fc.timeout = 20

print("List of latest FULL firmware by PRD:")

with open("prds.txt", "r") as afile:
    prdx = afile.read()
    prds = list(filter(None, prdx.split("\n")))

while len(prds) > 0:
    prd, lastver, model = prds[0].split(" ", 2)
    try:
        fc.reset_session()
        fc.curef = prd
        check_xml = fc.do_check()
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        txt_tv = tv
        if tv != lastver:
            txt_tv = tcllib.ANSI_WHITE + txt_tv + tcllib.ANSI_RESET
        print("{}: {} {} ({})".format(prd, txt_tv, fhash, model))
        prds.pop(0)
    except Timeout as e:
        print("{} failed. (Connection timed out.)".format(prd))
        print(tcllib.ANSI_UP_DEL, end="")
        continue
    except (SystemExit, RequestException) as e:
        print("{} failed. ({})".format(prd, str(e)))
        if e.response.status_code in [204, 404]:
            # No update available or invalid request - remove from queue
            prds.pop(0)
        else:
            print(tcllib.ANSI_UP_DEL, end="")
        continue
