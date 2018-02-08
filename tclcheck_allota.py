#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Check all/given PRDs for OTA updates."""

import sys

import tcllib
import tcllib.argparser
from tcllib import ansi, devlist
from tcllib.devices import MobileDevice
from tcllib.requests import RequestRunner, CheckRequest, ServerVoteSelector


dev = MobileDevice()

dpdesc = """
    Checks for the latest OTA updates for all PRD numbers or only for the PRD specified
    as prd. Initial software version can be specified with forcever.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("forcever", help="Initial software version to check for OTA updates, e.g. AAM481", nargs="?", default=None)
dp.add_argument("-p", "--prd", help="CU Reference # to filter scan results", dest="tocheck", nargs="?", default=None, metavar="PRD")
args = dp.parse_args(sys.argv[1:])

if args.forcever is not None:
    force_ver_text = " from {}".format(args.forcever)
else:
    force_ver_text = ""

prdcheck = "" if args.tocheck is None else args.tocheck

print("Loading list of devices.")
prds = devlist.get_devicelist()

print("List of latest OTA firmware{} by PRD:".format(force_ver_text))

runner = RequestRunner(ServerVoteSelector())
runner.max_tries = 20

for prd, variant in prds.items():
    model = variant["variant"]
    lastver = variant["last_ota"]
    lastver = variant["last_full"] if lastver is None else lastver
    if args.forcever is not None:
        lastver = args.forcever
    if not prdcheck in prd:
        continue
    dev.curef = prd
    dev.fwver = lastver
    chk = CheckRequest(dev)
    runner.run(chk)
    if chk.success:
        result = chk.get_result()
        versioninfo = ansi.YELLOW_DARK + result.fvver + ansi.RESET + " ⇨ " + ansi.YELLOW + result.tvver + ansi.RESET + " (FULL: {})".format(variant["last_full"])
        print("{}: {} {} ({})".format(prd, versioninfo, result.filehash, model))
    else:
        print("{} ({}): {}".format(prd, lastver, chk.error))

tcllib.FotaCheck.write_info_if_dumps_found()
