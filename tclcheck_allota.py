#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

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
args = dp.parse_args(sys.argv[1:])

if args.forcever is not None:
    force_ver_text = " from {}".format(args.forcever)
else:
    force_ver_text = ""

print("List of latest OTA firmware{} by PRD:".format(force_ver_text))

with open("prds.txt", "r") as f:
    for prdline in f:
        prdline = prdline.strip()
        prd, lastver, model = prdline.split(" ", 2)
        if args.forcever is not None:
            lastver = args.forcever
        try:
            fc.reset_session()
            fc.curef = prd
            fc.fv = lastver
            check_xml = fc.do_check(max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            print("{}: {} ⇨ {} {} ({})".format(prd, fv, tv, fhash, model))
        except RequestException as e:
            print("{} ({}): {}".format(prd, lastver, str(e)))
            continue
