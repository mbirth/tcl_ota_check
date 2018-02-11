#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Find new PRDs for a range of variants."""

import sys

from tcllib import ansi, argparser, devlist
from tcllib.devices import DesktopDevice
from tcllib.dumpmgr import write_info_if_dumps_found
from tcllib.requests import RequestRunner, CheckRequest, ServerVoteSelector


# Variants to scan for
SCAN_VARIANTS = ["001", "003", "009", "010", "700"]

dpdesc = """
    Finds new PRD numbers for a range of variants. Scan range can be set by
    floor and ceiling switches.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("floor", nargs="?", help="Model number to start with", type=int, default=63116)
dp.add_argument("ceiling", nargs="?", help="Model number to end with", type=int, default=99999)
dp.add_argument("-l", "--local", help="Force using local database", dest="local", action="store_true", default=False)
args = dp.parse_args(sys.argv[1:])

floor = args.floor
ceiling = args.ceiling + 1
if ceiling < floor:
    print("Invalid range!")
    raise SystemExit

print("Loading list of known devices...", end="", flush=True)
prd_db = devlist.get_devicelist(local=args.local)
print(" OK")

print("Valid PRDs not already in database:")

known_centers = set(int(x.replace("PRD-", "").split("-")[0]) for x in prd_db)
scan_list = set(range(floor, ceiling))

to_scan = scan_list - known_centers
total_count = len(to_scan) * len(SCAN_VARIANTS)
done_count = 0

dev = DesktopDevice()

runner = RequestRunner(ServerVoteSelector(), https=False)
runner.max_tries = 20

for center in to_scan:
    for j in SCAN_VARIANTS:
        curef = "PRD-{:05}-{:3}".format(center, j)
        done_count += 1
        print("Checking {} ({}/{})".format(curef, done_count, total_count))
        print(ansi.UP_DEL, end="")
        dev.curef = curef
        chk = CheckRequest(dev)
        runner.run(chk)
        if chk.success:
            chkres = chk.get_result()
            txt_tv = chkres.tvver
            print("{}: {} {}".format(curef, txt_tv, chkres.filehash))

print("Scan complete.")
write_info_if_dumps_found()
