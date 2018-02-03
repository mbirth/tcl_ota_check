#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Check all/given PRDs for OTA updates."""

import sys

from requests.exceptions import RequestException

import tcllib
import tcllib.argparser
from tcllib import ansi


fc = tcllib.FotaCheck()
fc.serid = "3531510"
#fc.osvs = "7.1.1"
fc.mode = fc.MODE.OTA
fc.cltp = fc.CLTP.MOBILE

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
prds = tcllib.FotaCheck.get_devicelist()

print("List of latest OTA firmware{} by PRD:".format(force_ver_text))

for prd, variant in prds.items():
    model = variant["variant"]
    lastver = variant["last_ota"]
    lastver = variant["last_full"] if lastver is None else lastver
    if args.forcever is not None:
        lastver = args.forcever
    if prdcheck in prd:
        try:
            fc.reset_session()
            fc.curef = prd
            fc.fv = lastver
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            versioninfo = ansi.YELLOW_DARK + fv + ansi.RESET + " ⇨ " + ansi.YELLOW + tv + ansi.RESET + " (FULL: {})".format(variant["last_full"])
            print("{}: {} {} ({})".format(prd, versioninfo, fhash, model))
        except RequestException as e:
            print("{} ({}): {}".format(prd, lastver, str(e)))
            continue

tcllib.FotaCheck.write_info_if_dumps_found()
