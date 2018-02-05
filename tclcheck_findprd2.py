#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Find new PRDs for a range of variants."""

import sys

from requests.exceptions import RequestException, Timeout

import tcllib
import tcllib.argparser
from tcllib import ansi
from tcllib import devlist


# Variants to scan for
SCAN_VARIANTS = ["001", "003", "009", "010", "700"]

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE.FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE.FULL)
#fc.cltp = fc.CLTP.MOBILE
fc.cltp = fc.CLTP.DESKTOP

dpdesc = """
    Finds new PRD numbers for a range of variants. Scan range can be set by
    floor and ceiling switches.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("floor", nargs="?", help="Model number to start with", type=int, default=63116)
dp.add_argument("ceiling", nargs="?", help="Model number to end with", type=int, default=99999)
args = dp.parse_args(sys.argv[1:])

floor = args.floor
ceiling = args.ceiling + 1
if ceiling < floor:
    print("Invalid range!")
    raise SystemExit

print("Loading list of known devices...", end="", flush=True)
prd_db = devlist.get_devicelist()
print(" OK")

print("Valid PRDs not already in database:")

known_centers = set(int(x.replace("PRD-", "").split("-")[0]) for x in prd_db)
scan_list = set(range(floor, ceiling))

to_scan = scan_list - known_centers
total_count = len(to_scan) * len(SCAN_VARIANTS)
done_count = 0

for center in to_scan:
    for j in SCAN_VARIANTS:
        curef = "PRD-{:05}-{:3}".format(center, j)
        done_count += 1
        print("Checking {} ({}/{})".format(curef, done_count, total_count))
        print(ansi.UP_DEL, end="")
        try:
            fc.reset_session()
            fc.curef = curef
            check_xml = fc.do_check(https=False, max_tries=20)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            txt_tv = tv
            print("{}: {} {}".format(curef, txt_tv, fhash))
        except (SystemExit, RequestException, Timeout) as e:
            continue

print("Scan complete.")
tcllib.FotaCheck.write_info_if_dumps_found()
