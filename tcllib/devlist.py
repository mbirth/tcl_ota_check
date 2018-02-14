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


def _load_local_devicelist():
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

def _download_devicelist(doit: bool):
    """Download device list if doit is set. Or do nothing."""
    if doit:
        prds_json = requests.get(DEVICELIST_URL).text
        with open(DEVICELIST_FILE, "wt") as dlfile:
            dlfile.write(prds_json)

def _load_devicelist_with_diff(output_diff: bool, old_prds: dict = {}) -> dict:
    """Load local devicelist and output diff if requested."""
    with open(DEVICELIST_FILE, "rt") as dlfile:
        prds = json.load(dlfile)

    if old_prds and output_diff:
        print_prd_diff(old_prds, prds)

    return prds

def get_devicelist(force: bool=False, output_diff: bool=True, local: bool=False) -> dict:
    """Return device list from saved database."""
    old_prds, need_download = _load_local_devicelist()

    if local:
        return old_prds

    _download_devicelist(need_download or force)

    return _load_devicelist_with_diff(output_diff, old_prds)


def print_versions_diff(old_data: dict, new_data: dict):
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

def _print_removed_prds(prds_data: dict, removed_prds: list):
    """Print details of selected PRDs as removed."""
    for prd in removed_prds:
        print("> Removed device {} (was at {} / OTA: {}).".format(ansi.RED + prd + ansi.RESET, prds_data[prd]["last_full"], prds_data[prd]["last_ota"]))

def _print_added_prds(prds_data: dict, added_prds: list):
    """Print details of selected PRDs as added."""
    for prd in added_prds:
        print("> New device {} ({} / OTA: {}).".format(ansi.GREEN + prd + ansi.RESET, prds_data[prd]["last_full"], prds_data[prd]["last_ota"]))

def _print_changed_prds(old_prds: dict, new_prds: dict, skip_prds: list):
    """Print details of changed PRDs."""
    for prd, pdata in new_prds.items():
        if prd in skip_prds:
            continue
        odata = old_prds[prd]
        print_versions_diff(odata, pdata)

def print_prd_diff(old_prds: dict, new_prds: dict):
    """Print PRD changes between old and new databases."""
    added_prds = [prd for prd in new_prds if prd not in old_prds]
    removed_prds = [prd for prd in old_prds if prd not in new_prds]
    _print_removed_prds(old_prds, removed_prds)
    _print_added_prds(new_prds, added_prds)
    _print_changed_prds(old_prds, new_prds, added_prds)
