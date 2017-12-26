#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import os
import random
import sys
import tcllib

fc = tcllib.FotaCheck()
fc.serid = "3531510"
#fc.osvs  = "7.1.1"

dp = tcllib.DefaultParser(__file__)
dp.description = """
    Checks for the latest FULL updates for the specified PRD number or for an OTA from the
    version specified as fvver.
    """
dp.add_argument("prd", nargs=1, help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("fvver", nargs="?", help="Firmware version to check for updates, e.g. AAM481", default="AAA000")
dp.add_argument("--mode", help="type of update to check for (auto, full, ota), defaults to auto", default="auto")
dp.add_argument("--type", help="type of check to run (auto, desktop, mobile), defaults to auto", default="auto")
args = dp.parse_args(sys.argv[1:])

def sel_mode(txtmode, autoval):
    if txtmode == "auto":
        return autoval
    elif txtmode == "ota":
        return fc.MODE.OTA
    return fc.MODE.FULL

def sel_cltp(txtmode, autoval):
    if txtmode == "auto":
        return autoval
    elif txtmode == "desktop":
        return fc.CLTP.DESKTOP
    return fc.CLTP.MOBILE

fc.curef = args.prd[0]
fc.fv = args.fvver
if args.fvver == "AAA000":
    fc.mode = sel_mode(args.mode, fc.MODE.FULL)
    fc.cltp = sel_cltp(args.type, fc.CLTP.DESKTOP)
else:
    fc.mode = sel_mode(args.mode, fc.MODE.OTA)
    fc.cltp = sel_cltp(args.type, fc.CLTP.MOBILE)

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
    headname = "header_{}.bin".format(tv)
    headdir = "headers"
    if not os.path.exists(headdir):
        os.makedirs(headdir)
    if len(header) == 4194320:
        print("Header length check passed. Writing to {}.".format(headname))
        with open(os.path.join(headdir, headname), "wb") as f:
            f.write(header)
    else:
        print("Header length invalid ({}).".format(len(header)))

tcllib.FotaCheck.write_info_if_dumps_found()
