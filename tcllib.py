# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import argparse
import base64
import binascii
import enum
import errno
import hashlib
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

ANSI_UP_DEL = u"\u001b[F\u001b[K"
ANSI_BLACK = u"\u001b[0;30m"
ANSI_RED_DARK = u"\u001b[0;31m"
ANSI_GREEN_DARK = u"\001b[0;32m"
ANSI_YELLOW_DARK = u"\u001b[0;33m"
ANSI_CYAN_DARK = u"\u001b[0;36m"
ANSI_SILVER = u"\u001b[0;37m"
ANSI_GREY = u"\u001b[1;30m"
ANSI_RED = u"\u001b[1;31m"
ANSI_GREEN = u"\001b[1;32m"
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
        outfile = "logs/{}.xml".format(self.get_salt())
        if not os.path.exists(os.path.dirname(outfile)):
            try:
                os.makedirs(os.path.dirname(outfile))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(outfile, "w") as f:
            f.write(data)

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
                    self.write_dump(req.text)
                    return req.text
                elif req.status_code == 204:
                    self.master_server_vote_on_time(reqtime, reqtime_avg)
                    raise requests.exceptions.HTTPError("No update available.", response=req)
                elif req.status_code == 404:
                    self.master_server_vote_on_time(reqtime, reqtime_avg)
                    raise requests.exceptions.HTTPError("No data for requested CUREF/FV combination.", response=req)
                elif req.status_code not in [500, 503]:
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
    def get_creds():
        creds = {
            b"YWNjb3VudA==": b"emhlbmdodWEuZ2Fv",
            b"cGFzc3dvcmQ=": b"cWFydUQ0b2s=",
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
        slave_list = root.find("SLAVE_LIST").findall("SLAVE")
        enc_list = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
        slaves = [s.text for s in slave_list]
        encslaves = [s.text for s in enc_list]
        return fileid, fileurl, slaves, encslaves

    def do_encrypt_header(self, encslave, address):
        params = self.get_creds()
        params[b"address"] = bytes(address, "utf-8")
        url = "https://" + encslave + "/encrypt_header.php"
        req = self.sess.post(url, data=params, verify=False)
        # Expect "HTTP 206 Partial Content" response
        if req.status_code == 206:
            return req.content
        else:
            print("ENCRYPT: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit
