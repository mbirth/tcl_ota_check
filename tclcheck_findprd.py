#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Find new PRDs for a given variant(s)."""

import collections
import sys

from requests.exceptions import RequestException, Timeout

import tcllib
import tcllib.argparser
from tcllib import ansi
from tcllib import devlist


fc = tcllib.FotaCheck()
fc.serid = "3531510"
fc.fv = "AAA000"
fc.mode = fc.MODE.FULL

# CLTP = 10 (only show actual updates or HTTP 206) / 2010 (always show latest version for MODE.FULL)
#fc.cltp = fc.CLTP.MOBILE
fc.cltp = fc.CLTP.DESKTOP

dpdesc = """
    Finds new PRD numbers for all known variants, or specified variants with tocheck. Scan range
    can be set by floor and ceiling switches.
    """
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("tocheck", help="CU Reference # to filter scan results", nargs="?", default=None)
dp.add_argument("-f", "--floor", help="Beginning of scan range", dest="floor", nargs="?", type=int, default=0)
dp.add_argument("-c", "--ceiling", help="End of scan range", dest="ceiling", nargs="?", type=int, default=999)
args = dp.parse_args(sys.argv[1:])

floor = args.floor
ceiling = args.ceiling + 1
if ceiling < floor:
    print("Invalid range!")
    raise SystemExit

print("Loading list of devices...", end="", flush=True)
prd_db = devlist.get_devicelist()
print(" OK")

print("Valid PRDs not already in database:")

prds = [x.replace("PRD-", "").split("-") for x in prd_db]
prdx = list({x[0]: x[1]} for x in prds)
prddict = collections.defaultdict(list)
for prdc in prdx:
    for key, value in prdc.items():
        prddict[key].append(value)

if args.tocheck is not None:
    args.tocheck = args.tocheck.replace("PRD-", "")
    prdkeys = list(prddict.keys())
    for k in prdkeys:
        if k != args.tocheck:
            del prddict[k]
    if not prddict:
        prddict[args.tocheck] = []

for center in sorted(prddict.keys()):
    tails = [int(i) for i in prddict[center]]
    safes = [g for g in range(floor, ceiling) if g not in tails]
    total_count = len(safes)
    done_count = 0
    print("Checking {} variant codes for model {}.".format(total_count, center))
    for j in safes:
        curef = "PRD-{}-{:03}".format(center, j)
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
