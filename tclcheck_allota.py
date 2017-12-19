#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import json
import requests
import sys
import tcllib
from requests.exceptions import RequestException

tcllib.make_escapes_work()

fc = tcllib.FotaCheck()
fc.serid = "3531510"
#fc.osvs  = "7.1.1"
fc.mode = fc.MODE.OTA
fc.cltp  = fc.CLTP.MOBILE

dp = tcllib.DefaultParser(__file__)
dp.add_argument("forcever", nargs="?", default=None)
dp.add_argument("-p", "--prd", dest="tocheck", nargs="?", default=None)
args = dp.parse_args(sys.argv[1:])

if args.forcever is not None:
    force_ver_text = " from {}".format(args.forcever)
else:
    force_ver_text = ""

prdcheck = "" if args.tocheck is None else args.tocheck 

print("Loading list of devices...", end="", flush=True)
prds = tcllib.FotaCheck.get_devicelist()
print(" OK")

print("List of latest OTA firmware{} by PRD:".format(force_ver_text))

for prd, variant in prds.items():
    model   = variant["variant"]
    lastver = variant["last_ota"]
    if lastver is None: lastver = variant["last_full"]
    if args.forcever is not None:
        lastver = args.forcever
    if prdcheck in prd:
        try:
            fc.reset_session()
            fc.curef = prd
            fc.fv = lastver
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            versioninfo = tcllib.ANSI_YELLOW_DARK + fv + tcllib.ANSI_RESET + " ⇨ " + tcllib.ANSI_YELLOW + tv + tcllib.ANSI_RESET + " (FULL: {})".format(variant["last_full"])
            print("{}: {} {} ({})".format(prd, versioninfo, fhash, model))
        except RequestException as e:
            print("{} ({}): {}".format(prd, lastver, str(e)))
            continue

tcllib.FotaCheck.write_info_if_dumps_found()
