#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import os
import random
import sys
import tcllib
import tcllib.argparser

fc = tcllib.FotaCheck()

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
dp = tcllib.argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("uri", help="URI to firmware, starts with '/body/...'")
args = dp.parse_args(sys.argv[1:])

fileurl = args.uri

# /body/ce570ddc079e2744558f191895e524d02a60476f/32/268932
#fileurl = "/body/ce570ddc079e2744558f191895e524d02a60476f/2c23717bb747f3c321195419f451de52efa8ea51/263790/268932"

chksum_xml = fc.do_checksum(random.choice(encslaves), fileurl, fileurl)
print(fc.pretty_xml(chksum_xml))
file_addr, sha1_body, sha1_enc_footer, sha1_footer = fc.parse_checksum(chksum_xml)
