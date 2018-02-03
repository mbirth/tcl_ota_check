#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import sys
import tcllib
import tcllib.argparser
from tcllib import ansi
from requests.exceptions import RequestException, Timeout

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.mode = fc.MODE.OTA

dpdesc = """
    Finds all valid OTA updates for a given PRD. Scan range can be set by
    startver and endver switches.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("prd", help="CU Reference #, e.g. PRD-63117-011")
dp.add_argument("startver", help="Beginning of scan range", nargs="?", default="AAA000")
dp.add_argument("endver", help="End of scan range", nargs="?", default="AAZ999")
args = dp.parse_args(sys.argv[1:])

fc.curef = args.prd
start_ver = args.startver
end_ver = args.endver

print("Valid firmwares for model {} (between {} and {}):".format(fc.curef, start_ver, end_ver))

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

done_count = 0
total_count = len(allvers)
for fv in allvers:
    done_count += 1
    print("Checking {} ({}/{})".format(fv, done_count, total_count))
    print(ansi.UP_DEL, end="")
    try:
        fc.reset_session()
        fc.fv = fv
        check_xml = fc.do_check(https=False, max_tries=20)
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        txt_tv = tv
        print("{}: {} ⇨ {} {}".format(curef, fv, txt_tv, fhash))
    except (SystemExit, RequestException, Timeout) as e:
        continue

print("Scan complete.")
tcllib.FotaCheck.write_info_if_dumps_found()
