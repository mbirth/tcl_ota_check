# -*- coding: utf-8 -*-

import time
from collections import OrderedDict

import requests
from defusedxml import ElementTree


class TclCheckMixin:
    def do_check(self, https=True, timeout=10, max_tries=5):
        protocol = "https://" if https else "http://"
        url = protocol + self.g2master + "/check.php"
        params = OrderedDict()
        params["id"] = self.serid
        params["curef"] = self.curef
        params["fv"] = self.fvver
        params["mode"] = self.mode.value
        params["type"] = self.ftype
        params["cltp"] = self.cltp.value
        params["cktp"] = self.cktp.value
        params["rtd"] = self.rtd.value
        params["chnl"] = self.chnl.value
        #params["osvs"] = self.osvs
        #params["ckot"] = self.ckot.value

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
                    req.encoding = "utf-8"    # Force encoding as server doesn't give one
                    self.write_dump(req.text)
                    return req.text
                elif req.status_code == 204:
                    self.master_server_vote_on_time(reqtime, reqtime_avg)
                    raise requests.exceptions.HTTPError("No update available.", response=req)
                elif req.status_code == 404:
                    self.master_server_vote_on_time(reqtime, reqtime_avg)
                    raise requests.exceptions.HTTPError("No data for requested CUREF/FV combination.", response=req)
                elif req.status_code not in [500, 502, 503]:
                    self.master_server_downvote()
                    req.raise_for_status()
                    raise requests.exceptions.HTTPError("HTTP {}.".format(req.status_code), response=req)
            except requests.exceptions.Timeout:
                pass
            # Something went wrong, try a different server
            self.master_server_downvote()
            self.g2master = self.get_master_server()
            protocol = "https://" if https else "http://"
            url = protocol + self.g2master + "/check.php"
        raise requests.exceptions.RetryError("Max tries ({}) reached.".format(max_tries), response=last_response)

    @staticmethod
    def parse_check(xmlstr):
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
