#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Find new PRDs for a given variant(s)."""

import collections
import sys

from tcllib import ansi, argparser, devlist
from tcllib.devices import DesktopDevice
from tcllib.dumpmgr import write_info_if_dumps_found
from tcllib.requests import CheckRequest, RequestRunner, ServerVoteSelector

dpdesc = """
    Finds new PRD numbers for all known variants, or specified variants with tocheck. Scan range
    can be set by floor and ceiling switches.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("tocheck", help="CU Reference #(s) to filter scan results", nargs="*", default=None)
dp.add_argument("-f", "--floor", help="Beginning of scan range", dest="floor", nargs="?", type=int, default=0)
dp.add_argument("-c", "--ceiling", help="End of scan range", dest="ceiling", nargs="?", type=int, default=999)
dp.add_argument("-l", "--local", help="Force using local database", dest="local", action="store_true", default=False)
dp.add_argument("-np", "--no-prefix", help="Skip 'PRD-' prefix", dest="noprefix", action="store_true", default=False)
dp.add_argument("-k2", "--key2", help="V2 syntax", dest="key2mode", action="store_true", default=False)
args = dp.parse_args(sys.argv[1:])

floor = args.floor
ceiling = args.ceiling + 1
if ceiling < floor:
    print("Invalid range!")
    raise SystemExit

print("Loading list of devices...", end="", flush=True)
prd_db = devlist.get_devicelist(local=args.local)
print(" OK")

print("Valid PRDs not already in database:")

prds = [x.replace("APBI-PRD", "").replace("PRD-", "").replace("-", "") for x in prd_db]
prdx = list({x[0:5]: x[5:]} for x in prds)
prddict = collections.defaultdict(list)
for prdc in prdx:
    for key, value in prdc.items():
        prddict[key].append(value)

if args.tocheck is not None:
    if not isinstance(args.tocheck, list):
        args.tocheck = [args.tocheck]
    args.tocheck = [toch.replace("APBI-PRD", "").replace("PRD-", "") for toch in args.tocheck]
    prdkeys = list(prddict.keys())
    for k in prdkeys:
        if k not in args.tocheck:
            del prddict[k]
    for toch in args.tocheck:
        if toch not in prddict.keys():
            prddict[toch] = []

dev = DesktopDevice()

runner = RequestRunner(ServerVoteSelector(), https=False)
runner.max_tries = 20

if args.key2mode:
    prefix = "APBI-PRD"
    suffix = ""
else:
    prefix = "" if args.noprefix else "PRD-"
    suffix = "-"

for center in sorted(prddict.keys()):
    tails = [int(i) for i in prddict[center]]
    safes = [g for g in range(floor, ceiling) if g not in tails]
    total_count = len(safes)
    done_count = 0
    print("Checking {} variant codes for model {}.".format(total_count, center))
    for j in safes:
        curef = "{}{}{}{:03}".format(prefix, center, suffix, j)
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
