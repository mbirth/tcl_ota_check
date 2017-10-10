#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

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

print("List of latest FULL firmware by PRD:")

with open("prds.txt", "rt") as f:
    for prdline in f:
        prdline = prdline.strip()
        prd, lastver, model = prdline.split(" ", 2)

        try:
            fc.reset_session()
            fc.curef = prd
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            txt_tv = tv
            if tv != lastver:
                txt_tv = tcllib.ANSI_CYAN + txt_tv + tcllib.ANSI_RESET + " (OTA: {})".format(lastver)
            print("{}: {} {} ({})".format(prd, txt_tv, fhash, model))
        except RequestException as e:
            print("{}: {}".format(prd, str(e)))
            continue
