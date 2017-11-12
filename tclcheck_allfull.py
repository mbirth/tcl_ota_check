#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import sys
import tcllib
from requests.exceptions import RequestException, Timeout

tcllib.make_escapes_work()

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE.FULL

dp = tcllib.DefaultParser(__file__)
dp.add_argument("-p", "--prd", dest="tocheck", nargs="?", default=None)
args = dp.parse_args(sys.argv[1:])

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE.FULL)
#fc.cltp  = fc.CLTP.MOBILE
fc.cltp  = fc.CLTP.DESKTOP

prdcheck = "" if args.tocheck is None else args.tocheck

print("List of latest FULL firmware by PRD:")

with open("prds.txt", "rt") as f:
    for prdline in f:
        prdline = prdline.strip()
        prd, lastver, model = prdline.split(" ", 2)
        if prdcheck in prd:
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

tcllib.FotaCheck.write_info_if_dumps_found()
