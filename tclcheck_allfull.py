#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Check all/given PRDs for FULL updates."""

import sys

from requests.exceptions import RequestException

import tcllib
import tcllib.argparser
from tcllib import ansi, devlist
from tcllib.devices import DesktopDevice


dev = DesktopDevice()
fc = tcllib.FotaCheck()

dpdesc = """
    Checks for the latest FULL updates for all PRD numbers or only for
    the PRD specified as prd.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("-p", "--prd", help="CU Reference # to filter scan results", dest="tocheck", nargs="?", default=None, metavar="PRD")
args = dp.parse_args(sys.argv[1:])

prdcheck = "" if args.tocheck is None else args.tocheck

print("Loading list of devices.")
prds = devlist.get_devicelist()

print("List of latest FULL firmware by PRD:")

for prd, variant in prds.items():
    model = variant["variant"]
    lastver = variant["last_full"]
    if prdcheck in prd:
        try:
            dev.curef = prd
            fc.reset_session(dev)
            check_xml = fc.do_check(dev, max_tries=20)
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
