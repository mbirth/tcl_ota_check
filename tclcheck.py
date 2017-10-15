#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import random
import sys
import tcllib

fc = tcllib.FotaCheck()
fc.cltp  = fc.CLTP.MOBILE
fc.serid = "3531510"
#fc.osvs  = "7.1.1"

dp = tcllib.DefaultParser(__file__)
dp.add_argument("prd", nargs="?", default="AAM481")
dp.add_argument("fvver", nargs="?", default="PRD-63117-011")
args = dp.parse_args(sys.argv[1:])

if len(sys.argv) == 3:  # python tclcheck.py $PRD $FV = OTA delta for $PRD from $FV
    fc.curef = args.prd
    fc.fv = args.fvver
    fc.mode  = fc.MODE.OTA
elif len(sys.argv) == 2:  # python tclcheck.py $PRD = FULL for $PRD
    fc.curef = args.prd
    fc.fv = "AAA000"
    fc.mode = fc.MODE.FULL
    fc.cltp  = fc.CLTP.DESKTOP
else:  # python tclcheck.py = OTA for default PRD, FV
    fc.curef = "PRD-63117-011"
    fc.fv    = "AAM481"
    fc.mode  = fc.MODE.OTA

check_xml = fc.do_check()
print(fc.pretty_xml(check_xml))
curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)

req_xml = fc.do_request(curef, fv, tv, fw_id)
print(fc.pretty_xml(req_xml))
fileid, fileurl, slaves, encslaves = fc.parse_request(req_xml)

for s in slaves:
    print("http://{}{}".format(s, fileurl))

if fc.mode == fc.MODE.FULL:
    header = fc.do_encrypt_header(random.choice(encslaves), fileurl)
    if len(header) == 4194320:
        print("Header length check passed. Writing to header_{}.bin.".format(tv))
        with open("header_{}.bin".format(tv), "wb") as f:
            f.write(header)
    else:
        print("Header length invalid ({}).".format(len(header)))
