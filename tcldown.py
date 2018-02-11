#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Download a given firmware file."""

import os
import sys

from tcllib import argparser
from tcllib.devices import DesktopDevice
from tcllib.requests import RequestRunner, CheckRequest, DownloadRequest, \
        ChecksumRequest, EncryptHeaderRequest, ServerSelector, \
        write_info_if_dumps_found


dpdesc = """
    Downloads the given firmware file.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("prd", nargs=1, help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("targetversion", nargs=1, help="Firmware version to download, e.g. AAN990")
dp.add_argument("fwid", nargs=1, help="Numeric firmware file id, e.g. 268932")
dp.add_argument("-o", "--ota", metavar="FROMVERSION", help="download OTA from specified version (switches mode to OTA)", type=str)
dp.add_argument("-i", "--imei", help="use specified IMEI instead of default", type=str)
dp.add_argument("-t", "--type", help="download device (default to desktop)", default="desktop", type=str, choices=["desktop", "mobile"])
dp.add_argument("--rawmode", help="override --mode with raw value (2=OTA, 4=FULL)", metavar="MODE")
dp.add_argument("--rawcltp", help="override --type with raw value (10=MOBILE, 2010=DESKTOP)", metavar="CLTP")
args = dp.parse_args(sys.argv[1:])

dev = DesktopDevice()

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

runner = RequestRunner(ServerSelector())
runner.max_tries = 20

tv = args.targetversion[0]
fw_id = args.fwid[0]
dlr = DownloadRequest(dev, tv, fw_id)
runner.run(dlr)
if not dlr.success:
    print("ERROR: {}".format(dlr.error))
    sys.exit(3)

dlrres = dlr.get_result()
print(dlrres.pretty_xml())

for s in dlrres.slaves:
    print("http://{}{}".format(s, dlrres.fileurl))

for s in dlrres.s3_slaves:
    print("http://{}{}".format(s, dlrres.s3_fileurl))

if dev.mode == dev.MODE_STATES["FULL"]:
    encrun = RequestRunner(ServerSelector(dlrres.encslaves), https=False)
    encrun.max_tries = 20
    hdr = EncryptHeaderRequest(dlrres.fileurl)
    encrun.run(hdr)
    if hdr.success:
        hdrres = hdr.get_result()
        headname = "header_{}.bin".format(tv)
        headdir = "headers"
        if not os.path.exists(headdir):
            os.makedirs(headdir)
        if len(hdrres.rawdata) == 4194320:
            print("Header length check passed. Writing to {}.".format(headname))
            with open(os.path.join(headdir, headname), "wb") as f:
                f.write(hdrres.rawdata)
        else:
            print("Header length invalid ({}).".format(len(hdrres.rawdata)))

write_info_if_dumps_found()
