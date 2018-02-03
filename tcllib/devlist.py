# -*- coding: utf-8 -*-

import json
import os
import time

import requests

from . import ansi


DEVICELIST_URL = "https://tclota.birth-online.de/json_lastupdates.php"
DEVICELIST_FILE = "prds.json"
DEVICELIST_CACHE_SECONDS = 86400


class DevListMixin:
    @staticmethod
    def get_devicelist(force=False, output_diff=True):
        need_download = True

        old_prds = None
        try:
            filestat = os.stat(DEVICELIST_FILE)
            filemtime = filestat.st_mtime
            if filemtime > time.time() - DEVICELIST_CACHE_SECONDS:
                need_download = False
            with open(DEVICELIST_FILE, "rt") as dlfile:
                old_prds = json.load(dlfile)
        except FileNotFoundError:
            pass

        if need_download or force:
            prds_json = requests.get(DEVICELIST_URL).text
            with open(DEVICELIST_FILE, "wt") as dlfile:
                dlfile.write(prds_json)

        with open(DEVICELIST_FILE, "rt") as dlfile:
            prds = json.load(dlfile)

        if old_prds and output_diff:
            DevListMixin.print_prd_diff(old_prds, prds)

        return prds

    @staticmethod
    def print_prd_diff(old_prds, new_prds):
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
            if pdata["last_full"] != odata["last_full"] and pdata["last_ota"] != odata["last_ota"]:
                print("> {}: {} ⇨ {} (OTA: {} ⇨ {})".format(
                    prd,
                    ansi.CYAN_DARK + str(odata["last_full"]) + ansi.RESET,
                    ansi.CYAN + str(pdata["last_full"]) + ansi.RESET,
                    ansi.YELLOW_DARK + str(odata["last_ota"]) + ansi.RESET,
                    ansi.YELLOW + str(pdata["last_ota"]) + ansi.RESET
                ))
            elif pdata["last_full"] != odata["last_full"]:
                print("> {}: {} ⇨ {} (FULL)".format(prd, ansi.CYAN_DARK + str(odata["last_full"]) + ansi.RESET, ansi.CYAN + str(pdata["last_full"]) + ansi.RESET))
            elif pdata["last_ota"] != odata["last_ota"]:
                print("> {}: {} ⇨ {} (OTA)".format(prd, ansi.YELLOW_DARK + str(odata["last_ota"]) + ansi.RESET, ansi.YELLOW + str(pdata["last_ota"]) + ansi.RESET))
