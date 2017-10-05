#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import sys
import tcllib
from requests.exceptions import RequestException, Timeout

tcllib.make_escapes_work()

fc = tcllib.FotaCheck()
fc.serid = "3531510"
#fc.osvs  = "7.1.1"
fc.mode = fc.MODE_OTA
fc.cltp  = 10
fc.timeout = 20

force_ver = False
force_ver_text = ""
if len(sys.argv) > 1:
    force_ver = sys.argv[1]
    force_ver_text = " from {}".format(force_ver)

print("List of latest OTA firmware{} by PRD:".format(force_ver_text))

with open("prds.txt", "r") as afile:
    prdx = afile.read()
    prds = list(filter(None, prdx.split("\n")))

while len(prds) > 0:
    prd, lastver, model = prds[0].split(" ", 2)
    if force_ver != False:
        lastver = force_ver
    try:
        fc.reset_session()
        fc.curef = prd
        fc.fv = lastver
        check_xml = fc.do_check()
        curef, fv, tv, fw_id, fileid, fn, fsize, fhash = fc.parse_check(check_xml)
        print("{}: {} ⇨ {} {} ({})".format(prd, fv, tv, fhash, model))
        prds.pop(0)
    except Timeout as e:
        print("{} failed. (Connection timed out.)".format(prd))
        print(tcllib.ANSI_UP_DEL, end="")
        continue
    except (SystemExit, RequestException) as e:
        print("{} ({}) failed. ({})".format(prd, lastver, str(e)))
        if e.response.status_code in [204, 404]:
            # No update available or invalid request - remove from queue
            prds.pop(0)
        else:
            print(tcllib.ANSI_UP_DEL, end="")
        continue
