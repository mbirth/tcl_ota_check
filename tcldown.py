#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Download a given firmware file."""

import os
import random
import sys

import tcllib
import tcllib.argparser
from tcllib.devices import DesktopDevice
from tcllib.xmltools import pretty_xml


fc = tcllib.FotaCheck()
dev = DesktopDevice()

dpdesc = """
    Downloads the given firmware file.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("prd", nargs=1, help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("targetversion", nargs=1, help="Firmware version to download, e.g. AAN990")
dp.add_argument("fwid", nargs=1, help="Numeric firmware file id, e.g. 268932")
dp.add_argument("-o", "--ota", metavar="FROMVERSION", help="download OTA from specified version (switches mode to OTA)", type=str)
dp.add_argument("-i", "--imei", help="use specified IMEI instead of default", type=str)
dp.add_argument("-t", "--type", help="download device (default to desktop)", default="desktop", type=str, choices=["desktop", "mobile"])
dp.add_argument("--rawmode", help="override --mode with raw value (2=OTA, 4=FULL)", metavar="MODE")
dp.add_argument("--rawcltp", help="override --type with raw value (10=MOBILE, 2010=DESKTOP)", metavar="CLTP")
args = dp.parse_args(sys.argv[1:])


def sel_mode(defaultmode, rawval):
    """Handle custom mode."""
    if rawval:
        return rawval
    return defaultmode


def sel_cltp(txtmode, rawval):
    """Handle custom CLTP."""
    if rawval:
        return rawval
    if txtmode == "mobile":
        return dev.CLTP_STATES["MOBILE"]
    return dev.CLTP_STATES["DESKTOP"]


if args.imei:
    print("Use specified IMEI: {}".format(args.imei))
    dev.imei = args.imei

dev.curef = args.prd[0]
if args.ota:
    dev.fwver = args.ota[0]
    dev.mode = sel_mode(dev.MODE_STATES["OTA"], args.rawmode)
else:
    dev.fwver = args.targetversion[0]
    dev.mode = sel_mode(dev.MODE_STATES["FULL"], args.rawmode)
dev.cltp = sel_cltp(args.type, args.rawcltp)

print("Mode: {}".format(dev.mode))
print("CLTP: {}".format(dev.cltp))

fv = dev.fwver
tv = args.targetversion[0]
fw_id = args.fwid[0]
req_xml = fc.do_request(dev.curef, fv, tv, fw_id)
print(pretty_xml(req_xml))
fileid, fileurl, slaves, encslaves, s3_fileurl, s3_slaves = fc.parse_request(req_xml)

for s in slaves:
    print("http://{}{}".format(s, fileurl))

for s in s3_slaves:
    print("http://{}{}".format(s, s3_fileurl))

if dev.mode == dev.MODE_STATES["FULL"]:
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
