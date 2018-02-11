#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Find all OTA updates for a given PRD."""

import sys

from tcllib import ansi, argparser, devlist
from tcllib.devices import MobileDevice
from tcllib.requests import RequestRunner, CheckRequest, ServerVoteSelector, \
        write_info_if_dumps_found


dpdesc = """
    Finds all valid OTA updates for a given PRD. Scan range can be set by
    startver and endver switches.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("prd", help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("startver", help="Beginning of scan range", nargs="?", default="AAA000")
dp.add_argument("endver", help="End of scan range", nargs="?", default="AAZ999")
args = dp.parse_args(sys.argv[1:])

dev = MobileDevice()
dev.curef = args.prd
start_ver = args.startver
end_ver = args.endver

print("Valid firmwares for model {} (between {} and {}):".format(dev.curef, start_ver, end_ver))

cur_ver = start_ver
allvers = []
while True:
    allvers.append(cur_ver)
    if cur_ver == end_ver:
        break
    letters = list(cur_ver[:3])
    num = int(cur_ver[3:6])
    num += 1
    if num > 999:
        num = 0
        for i in range(2, -1, -1):
            if letters[i] == "Z":
                letters[i] = "A"
                continue
            letters[i] = chr(ord(letters[i])+1)
            break
    cur_ver = "{:3}{:03d}".format("".join(letters), num)

runner = RequestRunner(ServerVoteSelector(), https=False)
runner.max_tries = 20

done_count = 0
total_count = len(allvers)
for fv in allvers:
    done_count += 1
    print("Checking {} ({}/{})".format(fv, done_count, total_count))
    print(ansi.UP_DEL, end="")
    dev.fwver = fv
    chk = CheckRequest(dev)
    runner.run(chk)
    if chk.success:
        chkres = chk.get_result()
        txt_tv = chkres.tvver
        print("{}: {} ⇨ {} {}".format(dev.curef, fv, txt_tv, chkres.filehash))

print("Scan complete.")
write_info_if_dumps_found()
