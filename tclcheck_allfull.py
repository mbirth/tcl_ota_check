#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Check all/given PRDs for FULL updates."""

import sys

import tcllib
import tcllib.argparser
from tcllib import ansi, devlist
from tcllib.devices import DesktopDevice
from tcllib.requests import RequestRunner, CheckRequest, ServerVoteSelector, write_info_if_dumps_found


dev = DesktopDevice()

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

runner = RequestRunner(ServerVoteSelector())
runner.max_tries = 20

for prd, variant in prds.items():
    model = variant["variant"]
    lastver = variant["last_full"]
    if not prdcheck in prd:
        continue
    dev.curef = prd
    chk = CheckRequest(dev)
    runner.run(chk)
    if chk.success:
        result = chk.get_result()
        txt_tv = result.tvver
        if result.tvver != lastver:
            txt_tv = "{} (old: {} / OTA: {})".format(
                ansi.CYAN + txt_tv + ansi.RESET,
                ansi.CYAN_DARK + variant["last_full"] + ansi.RESET,
                variant["last_ota"]
            )
        else:
            result.delete_dump()
        print("{}: {} {} ({})".format(prd, txt_tv, result.filehash, model))
    else:
        print("{}: {}".format(prd, str(chk.error)))

write_info_if_dumps_found()
