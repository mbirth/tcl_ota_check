#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import collections
import sys
import tcllib
from requests.exceptions import RequestException, Timeout

tcllib.make_escapes_work()

fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.mode = fc.MODE_OTA

if len(sys.argv) < 2:
    print("Syntax: {} PRD [STARTVER] [ENDVER]".format(sys.argv[0]))
    sys.exit()

start_ver = "AAA000"
end_ver = "AAZ999"
if len(sys.argv) >= 2:
    fc.curef = sys.argv[1]
if len(sys.argv) >= 3:
    start_ver = sys.argv[2]
if len(sys.argv) >= 4:
    end_ver = sys.argv[3]

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
    print(tcllib.ANSI_UP_DEL, end="")
    try:
        fc.reset_session()
        fc.fv = fv
        check_xml = fc.do_check(https=False, max_tries=3)
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        txt_tv = tv
        print("{}: {} ⇨ {} {}".format(curef, fv, txt_tv, fhash))
    except (SystemExit, RequestException, Timeout) as e:
        continue

print("Scan complete.")
