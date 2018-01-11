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
    Downloads the given firmware file.
    """
dp.add_argument("prd", nargs=1, help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("targetversion", nargs=1, help="Firmware version to download, e.g. AAN990")
dp.add_argument("fwid", nargs=1, help="Numeric firmware file id, e.g. 268932")
dp.add_argument("-o", "--ota", metavar="FROMVERSION", help="download OTA from specified version (switches mode to OTA)", type=str)
dp.add_argument("-i", "--imei", help="use specified IMEI instead of default", type=str)
dp.add_argument("-t", "--type", help="download device (default to desktop)", default="desktop", type=str, choices=["desktop", "mobile"])
dp.add_argument("--rawmode", help="override --mode with raw value (2=OTA, 4=FULL)")
dp.add_argument("--rawcltp", help="override --type with raw value (10=MOBILE, 2010=DESKTOP)")
args = dp.parse_args(sys.argv[1:])

def sel_mode(defaultmode, rawval):
    if rawval:
        enum = tcllib.default_enum("MODE", {"RAW": rawval})
        return enum.RAW
    return defaultmode

def sel_cltp(txtmode, rawval):
    if rawval:
        enum = tcllib.default_enum("CLTP", {"RAW": rawval})
        return enum.RAW
    if txtmode == "mobile":
        return fc.CLTP.MOBILE
    return fc.CLTP.DESKTOP

if args.imei:
    print("Use specified IMEI: {}".format(args.imei))
    fc.serid = args.imei

fc.curef = args.prd[0]
if args.ota:
    fc.fv   = args.ota[0]
    fc.mode = sel_mode(fc.MODE.OTA, args.rawmode)
else:
    fc.fv   = args.targetversion[0]
    fc.mode = sel_mode(fc.MODE.FULL, args.rawmode)
fc.cltp = sel_cltp(args.type, args.rawcltp)

print("Mode: {}".format(fc.mode.value))
print("CLTP: {}".format(fc.cltp.value))

fv = fc.fv
tv = args.targetversion[0]
fw_id = args.fwid[0]
req_xml = fc.do_request(fc.curef, fv, tv, fw_id)
print(fc.pretty_xml(req_xml))
fileid, fileurl, slaves, encslaves, s3_fileurl, s3_slaves = fc.parse_request(req_xml)

for s in slaves:
    print("http://{}{}".format(s, fileurl))

for s in s3_slaves:
    print("http://{}{}".format(s, s3_fileurl))

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
