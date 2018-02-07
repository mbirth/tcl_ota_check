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
from tcllib.xmltools import pretty_xml


fc = tcllib.FotaCheck()

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

fc.reset_session(dev)
check_xml = fc.do_check(dev)
print(pretty_xml(check_xml))
curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)

req_xml = fc.do_request(curef, fv, tv, fw_id)
print(pretty_xml(req_xml))
fileid, fileurl, slaves, encslaves, s3_fileurl, s3_slaves = fc.parse_request(req_xml)

if encslaves:
    chksum_xml = fc.do_checksum(random.choice(encslaves), fileurl, fileurl)
    print(pretty_xml(chksum_xml))
    file_addr, sha1_body, sha1_enc_footer, sha1_footer = fc.parse_checksum(chksum_xml)

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
        # TODO: Check sha1sum
        print("Header length check passed. Writing to {}.".format(headname))
        with open(os.path.join(headdir, headname), "wb") as f:
            f.write(header)
    else:
        print("Header length invalid ({}).".format(len(header)))

tcllib.FotaCheck.write_info_if_dumps_found()
