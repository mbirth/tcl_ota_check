#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import sys

from requests.exceptions import RequestException

import tcllib
import tcllib.argparser
from tcllib import ansi


fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE.FULL

dpdesc = """
    Checks for the latest FULL updates for all PRD numbers or only for
    the PRD specified as prd.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("-p", "--prd", help="CU Reference # to filter scan results", dest="tocheck", nargs="?", default=None, metavar="PRD")
args = dp.parse_args(sys.argv[1:])

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE.FULL)
#fc.cltp = fc.CLTP.MOBILE
fc.cltp = fc.CLTP.DESKTOP

prdcheck = "" if args.tocheck is None else args.tocheck

print("Loading list of devices.")
prds = tcllib.FotaCheck.get_devicelist()

print("List of latest FULL firmware by PRD:")

for prd, variant in prds.items():
    model = variant["variant"]
    lastver = variant["last_full"]
    if prdcheck in prd:
        try:
            fc.reset_session()
            fc.curef = prd
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            txt_tv = tv
            if tv != lastver:
                txt_tv = "{} (old: {} / OTA: {})".format(
                    ansi.CYAN + txt_tv + ansi.RESET,
                    ansi.CYAN_DARK + variant["last_full"] + ansi.RESET,
                    variant["last_ota"]
                )
            else:
                fc.delete_last_dump()
            print("{}: {} {} ({})".format(prd, txt_tv, fhash, model))
        except RequestException as e:
            print("{}: {}".format(prd, str(e)))
            continue

tcllib.FotaCheck.write_info_if_dumps_found()
