#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to interface with TCL's update request API."""

import time
from collections import OrderedDict, defaultdict

import requests
from defusedxml import ElementTree


class TclCheckMixin:
    """A mixin component for TCL's update request API."""

    def prep_check_url(self, https=True):
        """Prepare URL for update request."""
        protocol = "https://" if https else "http://"
        url = protocol + self.g2master + "/check.php"
        return url

    def prep_check(self, device=None, https=True):
        """Prepare URL and parameters for update request."""
        url = self.prep_check_url(https)
        params = OrderedDict()
        if device:
            # Need to support both ways for now
            params["id"] = device.imei
            params["curef"] = device.curef
            params["fv"] = device.fwver
            params["mode"] = device.mode
            params["type"] = device.type
            params["cltp"] = device.cltp
            params["cktp"] = device.cktp
            params["rtd"] = device.rtd
            params["chnl"] = device.chnl
            #params["osvs"] = device.osvs
            #params["ckot"] = device.ckot
        else:
            params["id"] = self.serid
            params["curef"] = self.curef
            params["fv"] = self.fv
            params["mode"] = self.mode.value
            params["type"] = self.ftype
            params["cltp"] = self.cltp.value
            params["cktp"] = self.cktp.value
            params["rtd"] = self.rtd.value
            params["chnl"] = self.chnl.value
            #params["osvs"] = self.osvs
            #params["ckot"] = self.ckot.value
        return url, params

    def do_check(self, device=None, https=True, timeout=10, max_tries=5):
        """Perform update request with given parameters."""
        url, params = self.prep_check(device, https)
        last_response = None
        for _ in range(0, max_tries):
            try:
                reqtime_start = time.perf_counter()
                req = self.sess.get(url, params=params, timeout=timeout)
                reqtime = time.perf_counter() - reqtime_start
                reqtime_avg = self.check_time_avg()
                self.check_time_add(reqtime)
                last_response = req
                if req.status_code == 200:
                    self.master_server_vote_on_time(reqtime, reqtime_avg)
                    req.encoding = "utf-8"  # Force encoding as server doesn't give one
                    self.write_dump(req.text)
                    return req.text
                elif req.status_code not in [500, 502, 503]:
                    self.do_check_errorhandle(req, reqtime, reqtime_avg)
            except requests.exceptions.Timeout:
                pass
            # Something went wrong, try a different server
            self.master_server_downvote()
            self.g2master = self.get_master_server()
            url = self.prep_check_url(https)
        raise requests.exceptions.RetryError("Max tries ({}) reached.".format(max_tries), response=last_response)

    def do_check_errorhandle(self, req, reqtime, reqtime_avg):
        """Handle non-HTTP 200 results for ``do_check``."""
        errcodes = defaultdict(lambda: "HTTP {}.".format(req.status_code))
        errcodes[204] = "No update available."
        errcodes[404] = "No data for requested CUREF/FV combination."
        if req.status_code in [204, 404]:
            self.master_server_vote_on_time(reqtime, reqtime_avg)
        elif req.status_code not in [500, 502, 503]:
            self.master_server_downvote()
            req.raise_for_status()
        raise requests.exceptions.HTTPError(errcodes[req.status_code], response=req)

    @staticmethod
    def parse_check(xmlstr):
        """Parse output of ``do_check``."""
        root = ElementTree.fromstring(xmlstr)
        curef = root.find("CUREF").text
        fvver = root.find("VERSION").find("FV").text
        tvver = root.find("VERSION").find("TV").text
        fw_id = root.find("FIRMWARE").find("FW_ID").text
        fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
        fileid = fileinfo.find("FILE_ID").text
        filename = fileinfo.find("FILENAME").text
        filesize = fileinfo.find("SIZE").text
        filehash = fileinfo.find("CHECKSUM").text
        return curef, fvver, tvver, fw_id, fileid, filename, filesize, filehash
