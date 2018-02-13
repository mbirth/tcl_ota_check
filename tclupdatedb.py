#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Update PRD database."""

import sys

from tcllib import argparser, devlist


dpdesc = """
    Updates PRD software database if local copy is outdated.
    """
dp = argparser.DefaultParser(__file__, dpdesc)
dp.add_argument("-f", "--force", help="force database update", dest="force", action="store_true", default=False)
args = dp.parse_args(sys.argv[1:])

print("Updating device database...")
prds = devlist.get_devicelist(force=args.force)
del prds
