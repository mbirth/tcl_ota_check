#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Return checksum for given firmware."""

import sys

from tcllib import argparser
from tcllib.requests import RequestRunner, ChecksumRequest, ServerSelector

encslaves = [
    "54.238.56.196",
    "46.51.183.28",
    "75.101.149.79",
    "54.249.227.45",
    "54.249.227.54",
    "54.225.78.202",
    "54.225.87.236",
    "54.195.239.239",
    "54.195.240.212",
]

dpdesc = """
    Returns the checksum for a given firmware URI.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("uri", help="URI to firmware, starts with '/body/...'")
args = dp.parse_args(sys.argv[1:])

fileurl = args.uri

# /body/ce570ddc079e2744558f191895e524d02a60476f/32/268932
#fileurl = "/body/ce570ddc079e2744558f191895e524d02a60476f/2c23717bb747f3c321195419f451de52efa8ea51/263790/268932"

runner = RequestRunner(ServerSelector(encslaves), https=False)

cks = ChecksumRequest(fileurl, fileurl)
runner.run(cks)

if not cks.success:
    print("{}".format(cks.error))
    sys.exit(4)
cksres = cks.get_result()
print(cksres.pretty_xml())
