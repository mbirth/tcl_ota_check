#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

# curl -v -H "Content-Type: text/plain" --data @test.xml http://example.org/tcl_update_db/

import glob
import os
import requests

# This is the URL to an installation of https://github.com/mbirth/tcl_update_db
UPLOAD_URL = "https://tclota.birth-online.de/"
LOGS_GLOB = os.path.normpath("logs/*.xml")

headers = { "Content-Type": "text/xml" }

for fn in glob.glob(LOGS_GLOB):
    print("Uploading {}…".format(fn), end="")
    with open(fn, "rb") as f:
        r = requests.post(UPLOAD_URL, data=f, headers=headers)
    if r.status_code == 200:
        os.remove(fn)
        print(" OK")
    else:
        add_text = ""
        if r.status_code in [413, 406, 412]:
            # File has been rejected by server, another try won't help
            os.remove(fn)
            add_text = " - Please try again later."
        print(" ERROR: HTTP {}{}".format(r.status_code, add_text))
