#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Checks for the latest FULL or OTA updates for specified PRD number."""

import os
import random
import sys

import tcllib
import tcllib.argparser
from tcllib.devices import Device
from tcllib.requests import RequestRunner, CheckRequest, DownloadRequest, ChecksumRequest, ServerSelector, write_info_if_dumps_found
from tcllib.xmltools import pretty_xml


dpdesc = """
    Checks for the latest FULL updates for the specified PRD number or for an OTA from the
    version specified as fvver.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("prd", nargs=1, help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("fvver", nargs="?", help="Firmware version to check for OTA updates, e.g. AAM481 (omit to run FULL check)", default="AAA000")
dp.add_argument("-i", "--imei", help="use specified IMEI instead of default", type=str)
dp.add_argument("-m", "--mode", help="force type of update to check for", default="auto", type=str, choices=["full", "ota"])
dp.add_argument("-t", "--type", help="force type of check to run", default="auto", type=str, choices=["desktop", "mobile"])
dp.add_argument("--rawmode", help="override --mode with raw value (2=OTA, 4=FULL)", metavar="MODE")
dp.add_argument("--rawcltp", help="override --type with raw value (10=MOBILE, 2010=DESKTOP)", metavar="CLTP")
args = dp.parse_args(sys.argv[1:])

dev = Device(args.prd[0], args.fvver)
dev.imei = "3531510"

def sel_mode(txtmode, autoval, rawval):
    """Handle custom mode."""
    if rawval:
        return rawval
    if txtmode == "auto":
        return autoval
    elif txtmode == "ota":
        return dev.MODE_STATES["OTA"]
    return dev.MODE_STATES["FULL"]

def sel_cltp(txtmode, autoval, rawval):
    """Handle custom CLTP."""
    if rawval:
        return rawval
    if txtmode == "auto":
        return autoval
    elif txtmode == "desktop":
        return dev.CLTP_STATES["DESKTOP"]
    return dev.CLTP_STATES["MOBILE"]

if args.imei:
    print("Use specified IMEI: {}".format(args.imei))
    dev.imei = args.imei

if args.fvver == "AAA000":
    dev.mode = sel_mode(args.mode, dev.MODE_STATES["FULL"], args.rawmode)
    dev.cltp = sel_cltp(args.type, dev.CLTP_STATES["DESKTOP"], args.rawcltp)
else:
    dev.mode = sel_mode(args.mode, dev.MODE_STATES["OTA"], args.rawmode)
    dev.cltp = sel_cltp(args.type, dev.CLTP_STATES["MOBILE"], args.rawcltp)

print("Mode: {}".format(dev.mode))
print("CLTP: {}".format(dev.cltp))

runner = RequestRunner(ServerSelector())

# Check for update
chk = CheckRequest(dev)
runner.run(chk)
if not chk.success:
    print("{}".format(chk.error))
    sys.exit(2)
chkres = chk.get_result()
print(chkres.pretty_xml())

# Request download
dlr = DownloadRequest(dev, chkres.tvver, chkres.fw_id)
runner.run(dlr)
if not dlr.success:
    print("{}".format(dlr.error))
    sys.exit(3)
dlrres = dlr.get_result()
print(dlrres.pretty_xml())

if dlrres.encslaves:
    cksrunner = RequestRunner(ServerSelector(dlrres.encslaves), https=False)
    cks = ChecksumRequest(dlrres.fileurl, dlrres.fileurl)
    cksrunner.run(cks)
    if not cks.success:
        print("{}".format(cks.error))
        sys.exit(4)
    cksres = cks.get_result()
    print(cksres.pretty_xml())

for s in dlrres.slaves:
    print("http://{}{}".format(s, dlrres.fileurl))

for s in dlrres.s3_slaves:
    print("http://{}{}".format(s, dlrres.s3_fileurl))

if dev.mode == dev.MODE_STATES["FULL"]:
    header = fc.do_encrypt_header(random.choice(encslaves), fileurl)
    headname = "header_{}.bin".format(tv)
    headdir = "headers"
    if not os.path.exists(headdir):
        os.makedirs(headdir)
    if len(header) == 4194320:
        # TODO: Check sha1sum
        print("Header length check passed. Writing to {}.".format(headname))
        with open(os.path.join(headdir, headname), "wb") as f:
            f.write(header)
    else:
        print("Header length invalid ({}).".format(len(header)))

tcllib.FotaCheck.write_info_if_dumps_found()
