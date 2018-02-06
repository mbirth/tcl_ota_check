#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to manage saved device databases."""

import json
import os
import time

import requests

from . import ansi


DEVICELIST_URL = "https://tclota.birth-online.de/json_lastupdates.php"
DEVICELIST_FILE = "prds.json"
DEVICELIST_CACHE_SECONDS = 86400


def load_local_devicelist():
    """Load local devicelist and return decoded JSON (or None) and need_download status."""
    need_download = True
    try:
        filestat = os.stat(DEVICELIST_FILE)
        filemtime = filestat.st_mtime
        if filemtime > time.time() - DEVICELIST_CACHE_SECONDS:
            need_download = False
        with open(DEVICELIST_FILE, "rt") as dlfile:
            return json.load(dlfile), need_download
    except FileNotFoundError:
        return None, True


def get_devicelist(force=False, output_diff=True):
    """Return device list from saved database."""
    old_prds, need_download = load_local_devicelist()

    if need_download or force:
        prds_json = requests.get(DEVICELIST_URL).text
        with open(DEVICELIST_FILE, "wt") as dlfile:
            dlfile.write(prds_json)

    with open(DEVICELIST_FILE, "rt") as dlfile:
        prds = json.load(dlfile)

    if old_prds and output_diff:
        print_prd_diff(old_prds, prds)

    return prds


def print_versions_diff(old_data, new_data):
    """Print version changes between old and new databases."""
    prd = new_data["curef"]
    if new_data["last_full"] != old_data["last_full"] and new_data["last_ota"] != old_data["last_ota"]:
        print("> {}: {} ⇨ {} (OTA: {} ⇨ {})".format(
            prd,
            ansi.CYAN_DARK + str(old_data["last_full"]) + ansi.RESET,
            ansi.CYAN + str(new_data["last_full"]) + ansi.RESET,
            ansi.YELLOW_DARK + str(old_data["last_ota"]) + ansi.RESET,
            ansi.YELLOW + str(new_data["last_ota"]) + ansi.RESET
        ))
    elif new_data["last_full"] != old_data["last_full"]:
        print("> {}: {} ⇨ {} (FULL)".format(prd, ansi.CYAN_DARK + str(old_data["last_full"]) + ansi.RESET, ansi.CYAN + str(new_data["last_full"]) + ansi.RESET))
    elif new_data["last_ota"] != old_data["last_ota"]:
        print("> {}: {} ⇨ {} (OTA)".format(prd, ansi.YELLOW_DARK + str(old_data["last_ota"]) + ansi.RESET, ansi.YELLOW + str(new_data["last_ota"]) + ansi.RESET))


def print_prd_diff(old_prds, new_prds):
    """Print PRD changes between old and new databases."""
    added_prds = [prd for prd in new_prds if prd not in old_prds]
    removed_prds = [prd for prd in old_prds if prd not in new_prds]
    for prd in removed_prds:
        print("> Removed device {} (was at {} / OTA: {}).".format(ansi.RED + prd + ansi.RESET, old_prds[prd]["last_full"], old_prds[prd]["last_ota"]))
    for prd in added_prds:
        print("> New device {} ({} / OTA: {}).".format(ansi.GREEN + prd + ansi.RESET, new_prds[prd]["last_full"], new_prds[prd]["last_ota"]))
    for prd, pdata in new_prds.items():
        if prd in added_prds:
            continue
        odata = old_prds[prd]
        print_versions_diff(odata, pdata)
