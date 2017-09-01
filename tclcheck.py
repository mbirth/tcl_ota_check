#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import tcllib
import random
import sys

fc = tcllib.FotaCheck()
if len(sys.argv) == 3:  # python tclcheck.py $PRD $FV = OTA delta for $PRD from $FV
    fc.curef = sys.argv[1]
    fc.fv = sys.argv[2]
    fc.mode  = fc.MODE_OTA
elif len(sys.argv) == 2:  # python tclcheck.py $PRD = FULL for $PRD
    fc.curef = sys.argv[1]
    fc.fv = "AAM481"
    fc.mode = fc.MODE_FULL
else:  # python tclcheck.py = OTA for default PRD, FV
    fc.curef = "PRD-63117-011"
    fc.fv    = "AAM481"
    fc.mode  = fc.MODE_OTA
fc.serid = "3531510"
#fc.osvs  = "7.1.1"
fc.cltp  = 10
#fc.cltp  = 2010

check_xml = fc.do_check()
print(fc.pretty_xml(check_xml))
curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)

req_xml = fc.do_request(curef, fv, tv, fw_id)
print(fc.pretty_xml(req_xml))
fileid, fileurl, slaves, encslaves = fc.parse_request(req_xml)

for s in slaves:
    print("http://{}{}".format(s, fileurl))

if fc.mode == fc.MODE_FULL:
    print(fc.encrypt_header(fileurl, random.choice(encslaves)))
