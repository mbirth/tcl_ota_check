# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import argparse
import base64
import binascii
import enum
import errno
import glob
import hashlib
import json
import os
import platform
import random
import time
import xml.dom.minidom
import zlib
from collections import OrderedDict
from math import floor
import numpy
import requests
from defusedxml import ElementTree

DEVICELIST_URL = "https://tclota.birth-online.de/json_lastupdates.php"
DEVICELIST_FILE = "prds.json"
DEVICELIST_CACHE_SECONDS = 86400

ANSI_UP_DEL = u"\u001b[F\u001b[K"
ANSI_BLACK = u"\u001b[0;30m"
ANSI_RED_DARK = u"\u001b[0;31m"
ANSI_GREEN_DARK = u"\u001b[0;32m"
ANSI_YELLOW_DARK = u"\u001b[0;33m"
ANSI_CYAN_DARK = u"\u001b[0;36m"
ANSI_SILVER = u"\u001b[0;37m"
ANSI_GREY = u"\u001b[1;30m"
ANSI_RED = u"\u001b[1;31m"
ANSI_GREEN = u"\u001b[1;32m"
ANSI_YELLOW = u"\u001b[1;33m"
ANSI_CYAN = u"\u001b[1;36m"
ANSI_WHITE = u"\u001b[1;37m"
ANSI_RESET = u"\u001b[0m"

def make_escapes_work():
    system = platform.system()
    if system == "Windows":
        try:
            import colorama
        except ImportError:
            pass
        else:
            colorama.init()


def default_enum(enumname, vardict):
    return enum.IntEnum(enumname, vardict, module=__name__, qualname="tcllib.FotaCheck.{}".format(enumname))


class DefaultParser(argparse.ArgumentParser):
    def __init__(self, appname):
        super().__init__(prog=appname.replace(".py", ""), epilog="https://github.com/mbirth/tcl_ota_check")


class FotaCheck:
    VDKEY = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"
    CKTP = default_enum("CKTP", ["AUTO", "MANUAL"])
    MODE = default_enum("MODE", {"OTA": 2, "FULL": 4})
    RTD = default_enum("RTD", ["UNROOTED", "ROOTED"])
    CHNL = default_enum("CHNL", ["3G", "WIFI"])
    CLTP = default_enum("CLTP", {"MOBILE": 10, "DESKTOP": 2010})
    CKOT = default_enum("CKOT", ["ALL", "AOTA_ONLY", "FOTA_ONLY"])

    def __init__(self):
        self.serid = "543212345000000"
        self.curef = "PRD-63117-011"
        self.fv    = "AAM481"
        self.osvs  = "7.1.1"
        self.mode  = self.MODE.FULL
        self.ftype = "Firmware"
        self.cltp  = self.CLTP.MOBILE
        self.cktp  = self.CKTP.MANUAL
        self.ckot  = self.CKOT.ALL
        self.rtd   = self.RTD.UNROOTED
        self.chnl  = self.CHNL.WIFI
        self.g2master = None
        self.master_servers = [
            "g2master-us-east.tclclouds.com",
            "g2master-us-west.tclclouds.com",
            "g2master-eu-west.tclclouds.com",
            "g2master-ap-south.tclclouds.com",
            "g2master-ap-north.tclclouds.com",
            "g2master-sa-east.tclclouds.com",
        ]
        self.master_servers_weights = [3] * len(self.master_servers)
        self.check_time_sum = 3
        self.check_time_count = 1
        self.reset_session()

    def reset_session(self):
        self.g2master = self.get_master_server()
        self.sess = requests.Session()
        if self.mode == self.MODE.FULL:
            self.sess.headers.update({"User-Agent": "com.tcl.fota/5.1.0.2.0029.0, Android"})
        else:
            self.sess.headers.update({"User-Agent": "tcl"})
        return self.sess

    @staticmethod
    def get_salt():
        millis = floor(time.time() * 1000)
        tail = "{:06d}".format(random.randint(0, 999999))
        return "{}{}".format(str(millis), tail)

    def get_master_server(self):
        weight_sum = 0
        for i in self.master_servers_weights:
            weight_sum += i
        numpy_weights = []
        for i in self.master_servers_weights:
            numpy_weights.append(i/weight_sum)
        return numpy.random.choice(self.master_servers, p=numpy_weights)

    def master_server_downvote(self):
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] > 1:
            self.master_servers_weights[idx] -= 1

    def master_server_upvote(self):
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] < 10:
            self.master_servers_weights[idx] += 1

    def check_time_add(self, duration):
        self.check_time_sum += duration
        self.check_time_count += 1

    def check_time_avg(self):
        return (self.check_time_sum / self.check_time_count)

    def master_server_vote_on_time(self, last_duration, avg_duration):
        if last_duration < avg_duration - 0.5:
            self.master_server_upvote()
        elif last_duration > avg_duration + 0.5:
            self.master_server_downvote()

    def write_dump(self, data):
        outfile = os.path.normpath("logs/{}.xml".format(self.get_salt()))
        if not os.path.exists(os.path.dirname(outfile)):
            try:
                os.makedirs(os.path.dirname(outfile))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(data)

    @staticmethod
    def write_info_if_dumps_found():
        # To disable this info, uncomment the following line.
        #return
        files = glob.glob(os.path.normpath("logs/*.xml"))
        if len(files) > 0:
            print()
            print("{}There are {} logs collected in the logs/ directory.{} Please consider uploading".format(ANSI_YELLOW, len(files), ANSI_RESET))
            print("them to https://tclota.birth-online.de/ by running {}./upload_logs.py{}.".format(ANSI_CYAN, ANSI_RESET))

    def do_check(self, https=True, timeout=10, max_tries=5):
        protocol = "https://" if https else "http://"
        url = protocol + self.g2master + "/check.php"
        params = OrderedDict()
        params["id"]    = self.serid
        params["curef"] = self.curef
        params["fv"]    = self.fv
        params["mode"]  = self.mode.value
        params["type"]  = self.ftype
        params["cltp"]  = self.cltp.value
        params["cktp"]  = self.cktp.value
        params["rtd"]   = self.rtd.value
        params["chnl"]  = self.chnl.value
        #params["osvs"]  = self.osvs
        #params["ckot"]  = self.ckot.value

        last_response = None
        for num_try in range(0, max_tries):
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
    def pretty_xml(xmlstr):
        mdx = xml.dom.minidom.parseString(xmlstr)
        return mdx.toprettyxml(indent="  ")

    @staticmethod
    def parse_check(xmlstr):
        root = ElementTree.fromstring(xmlstr)
        curef = root.find("CUREF").text
        fv = root.find("VERSION").find("FV").text
        tv = root.find("VERSION").find("TV").text
        fw_id = root.find("FIRMWARE").find("FW_ID").text
        fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
        fileid   = fileinfo.find("FILE_ID").text
        filename = fileinfo.find("FILENAME").text
        filesize = fileinfo.find("SIZE").text
        filehash = fileinfo.find("CHECKSUM").text
        return curef, fv, tv, fw_id, fileid, filename, filesize, filehash

    def get_vk2(self, params_dict, cltp):
        params_dict["cltp"] = cltp
        query = ""
        for k, v in params_dict.items():
            if len(query) > 0:
                query += "&"
            query += k + "=" + str(v)
        vdk = zlib.decompress(binascii.a2b_base64(self.VDKEY))
        query += vdk.decode("utf-8")
        engine = hashlib.sha1()
        engine.update(bytes(query, "utf-8"))
        hexhash = engine.hexdigest()
        return hexhash

    @staticmethod
    def get_devicelist(force=False, output_diff=True):
        need_download = True

        old_prds = None
        try:
            filestat = os.stat(DEVICELIST_FILE)
            filemtime = filestat.st_mtime
            if filemtime > time.time() - DEVICELIST_CACHE_SECONDS:
                need_download = False
            with open(DEVICELIST_FILE, "rt") as df:
                old_prds = json.load(df)
        except FileNotFoundError:
            pass

        if need_download or force:
            prds_json = requests.get(DEVICELIST_URL).text
            with open(DEVICELIST_FILE, "wt") as df:
                df.write(prds_json)

        with open(DEVICELIST_FILE, "rt") as df:
            prds = json.load(df)

        if old_prds and output_diff:
            FotaCheck.print_prd_diff(old_prds, prds)

        return prds

    @staticmethod
    def print_prd_diff(old_prds, new_prds):
        added_prds = [prd for prd in new_prds if prd not in old_prds]
        removed_prds = [prd for prd in old_prds if prd not in new_prds]
        for prd in removed_prds:
            print("> Removed device {} (was at {} / OTA: {}).".format(ANSI_RED + prd + ANSI_RESET, old_prds[prd]["last_full"], old_prds[prd]["last_ota"]))
        for prd in added_prds:
            print("> New device {} ({} / OTA: {}).".format(ANSI_GREEN + prd + ANSI_RESET, new_prds[prd]["last_full"], new_prds[prd]["last_ota"]))
        for prd, pdata in new_prds.items():
            if prd in added_prds:
                continue
            odata = old_prds[prd]
            if pdata["last_full"] != odata["last_full"] and pdata["last_ota"] != odata["last_ota"]:
                print("> {}: {} ⇨ {} (OTA: {} ⇨ {})".format(
                    prd,
                    ANSI_CYAN_DARK + str(odata["last_full"]) + ANSI_RESET,
                    ANSI_CYAN + str(pdata["last_full"]) + ANSI_RESET,
                    ANSI_YELLOW_DARK + str(odata["last_ota"]) + ANSI_RESET,
                    ANSI_YELLOW + str(pdata["last_ota"]) + ANSI_RESET
                ))
            elif pdata["last_full"] != odata["last_full"]:
                print("> {}: {} ⇨ {} (FULL)".format(prd, ANSI_CYAN_DARK + str(odata["last_full"]) + ANSI_RESET, ANSI_CYAN + str(pdata["last_full"]) + ANSI_RESET))
            elif pdata["last_ota"] != odata["last_ota"]:
                print("> {}: {} ⇨ {} (OTA)".format(prd, ANSI_YELLOW_DARK + str(odata["last_ota"]) + ANSI_RESET, ANSI_YELLOW + str(pdata["last_ota"]) + ANSI_RESET))

    @staticmethod
    def get_creds():
        creds = {
            b"YWNjb3VudA==": b"emhlbmdodWEuZ2Fv",
            b"cGFzc3dvcmQ=": b"cWFydUQ0b2s=",
        }
        params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
        return params

    @staticmethod
    def get_creds2():
        creds = {
            b"YWNjb3VudA==": b"VGVsZUV4dFRlc3Q=",
            b"cGFzc3dvcmQ=": b"dDA1MjM=",
        }
        params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
        return params

    '''
        private HashMap<String, String> buildDownloadUrisParams(UpdatePackageInfo updatePackageInfo) {
            FotaLog.m28v(TAG, "doAfterCheck");
            String salt = FotaUtil.salt();
            HashMap linkedHashMap = new LinkedHashMap();
            linkedHashMap.put("id", this.internalBuilder.getParam("id"));
            linkedHashMap.put("salt", salt);
            linkedHashMap.put("curef", updatePackageInfo.mCuref);
            linkedHashMap.put("fv", updatePackageInfo.mFv);
            linkedHashMap.put("tv", updatePackageInfo.mTv);
            linkedHashMap.put("type", "Firmware");
            linkedHashMap.put("fw_id", updatePackageInfo.mFirmwareId);
            linkedHashMap.put("mode", "2");
            linkedHashMap.put("vk", generateVk2((LinkedHashMap) linkedHashMap.clone()));
            linkedHashMap.put("cltp", "10");
            linkedHashMap.put("cktp", this.internalBuilder.getParam("cktp"));
            linkedHashMap.put("rtd", this.internalBuilder.getParam("rtd"));
            linkedHashMap.put("chnl", this.internalBuilder.getParam("chnl"));
            return linkedHashMap;
        }
    '''

    def do_request(self, curef, fv, tv, fw_id):
        url = "https://" + self.g2master + "/download_request.php"
        params = OrderedDict()
        params["id"]    = self.serid
        params["salt"]  = self.get_salt()
        params["curef"] = curef
        params["fv"]    = fv
        params["tv"]    = tv
        params["type"]  = self.ftype
        params["fw_id"] = fw_id
        params["mode"]  = self.mode.value
        params["vk"]    = self.get_vk2(params, self.cltp.value)
        params["cltp"]  = self.cltp.value
        params["cktp"]  = self.cktp.value
        params["rtd"]   = self.rtd.value
        if self.mode == self.MODE.FULL:
            params["foot"]  = 1
        params["chnl"]  = self.chnl.value

        #print(repr(dict(params)))
        req = self.sess.post(url, data=params)
        if req.status_code == 200:
            req.encoding = "utf-8"    # Force encoding as server doesn't give one
            self.write_dump(req.text)
            return req.text
        else:
            print("REQUEST: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit

    @staticmethod
    def parse_request(xmlstr):
        root = ElementTree.fromstring(xmlstr)
        file = root.find("FILE_LIST").find("FILE")
        fileid  = file.find("FILE_ID").text
        fileurl = file.find("DOWNLOAD_URL").text
        s3_fileurl = file.find("S3_DOWNLOAD_URL").text
        slave_list = root.find("SLAVE_LIST").findall("SLAVE")
        enc_list = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
        s3_slave_list = root.find("SLAVE_LIST").findall("S3_SLAVE")
        slaves = [s.text for s in slave_list]
        encslaves = [s.text for s in enc_list]
        s3_slaves = [s.text for s in s3_slave_list]
        return fileid, fileurl, slaves, encslaves, s3_fileurl, s3_slaves

    def do_encrypt_header(self, encslave, address):
        params = self.get_creds2()
        params[b"address"] = bytes(address, "utf-8")
        url = "http://" + encslave + "/encrypt_header.php"
        req = self.sess.post(url, data=params, verify=False)
        # Expect "HTTP 206 Partial Content" response
        if req.status_code == 206:
            return req.content
        else:
            print("ENCRYPT: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit

    def do_checksum(self, encslave, address, uri):
        url = "http://" + encslave + "/checksum.php"
        params = self.get_creds2()

        payload = {address: uri}
        payload_json = json.dumps(payload)
        params[b"address"]  = bytes(payload_json, "utf-8")

        #print(repr(dict(params)))
        req = self.sess.post(url, data=params)
        if req.status_code == 200:
            req.encoding = "utf-8"    # Force encoding as server doesn't give one
            self.write_dump(req.text)
            # <ENCRYPT_FOOTER>2abfa6f6507044fec995efede5d818e62a0b19b5</ENCRYPT_FOOTER> means ERROR (invalid ADDRESS!)
            return req.text
        else:
            print("CHECKSUM: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit

    @staticmethod
    def parse_checksum(xmlstr):
        root = ElementTree.fromstring(xmlstr)
        file = root.find("FILE_CHECKSUM_LIST").find("FILE")
        file_addr = file.find("ADDRESS").text
        sha1_enc_footer = file.find("ENCRYPT_FOOTER").text
        sha1_footer = file.find("FOOTER").text
        sha1_body = file.find("BODY").text
        return file_addr, sha1_body, sha1_enc_footer, sha1_footer
