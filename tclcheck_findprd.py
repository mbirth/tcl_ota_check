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
fc.fv = "AAA000"
fc.mode = fc.MODE_FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE_FULL)
#fc.cltp  = 10
fc.cltp  = 2010

dp = tcllib.DefaultParser(__file__)
dp.add_argument("tocheck", nargs="?", default=None)
dp.add_argument("-f", "--floor", dest="floor", nargs="?", type=int, default=0)
dp.add_argument("-c", "--ceiling", dest="ceiling", nargs="?", type=int, default=999)
args = dp.parse_args(sys.argv[1:])

floor = args.floor
ceiling = args.ceiling + 1
if ceiling < floor:
    print("Invalid range!")
    raise SystemExit

print("Valid PRDs not already in database:")

with open("prds.txt", "r") as afile:
    prddict = collections.defaultdict(list)
    prda = afile.readlines()
    prds = [x.split(" ")[0].replace("PRD-", "").split("-") for x in prda]
    prdx = list({x[0]: x[1]} for x in prds)
    for prdc in prdx:
        for key, value in prdc.items():
            prddict[key].append(value)

if args.tocheck is not None:
    prdkeys = list(prddict.keys())
    for k in prdkeys:
        if k != args.tocheck:
            del prddict[k]
    if not prddict:
        prddict[args.tocheck] = []

for center in sorted(prddict.keys()):
    alltails = [int(i) for i in prddict[center]]
    tails = [h for h in alltails if floor < h < ceiling]
    safes = [g for g in range(floor, ceiling) if g not in alltails]
    while True:
        if floor in alltails:
            floor += 1
        else:
            break
    total_count = len(safes)
    done_count = 0
    print("Checking {} variant codes for model {}.".format(total_count, center))
    for j in range(floor, ceiling):
        if j in tails:
            continue
        curef = "PRD-{}-{:03}".format(center, j)
        done_count += 1
        print("Checking {} ({}/{})".format(curef, done_count, total_count))
        print(tcllib.ANSI_UP_DEL, end="")
        try:
            fc.reset_session()
            fc.curef = curef
            check_xml = fc.do_check(https=False, max_tries=3)
            curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
            txt_tv = tv
            print("{}: {} {}".format(curef, txt_tv, fhash))
        except (SystemExit, RequestException, Timeout) as e:
            continue

print("Scan complete.")
