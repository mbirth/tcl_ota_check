# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import base64
import binascii
import hashlib
import platform
import random
import time
import xml.dom.minidom
import zlib
from collections import OrderedDict
from math import floor
try:
    from defusedxml import ElementTree
except (ImportError, AttributeError):
    from xml.etree import ElementTree
import requests

ANSI_UP_DEL = u"\u001b[F\u001b[K"
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


class FotaCheck:
    VDKEY = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"
    CKTP_CHECKAUTO = 1
    CKTP_CHECKMANUAL = 2
    MODE_OTA = 2
    MODE_FULL = 4
    RTD_ROOTED = 2
    RTD_UNROOTED = 1
    CHNL_WIFI = 2
    CHNL_3G = 1

    def __init__(self):
        self.serid = "543212345000000"
        self.curef = "PRD-63117-011"
        self.fv    = "AAM481"
        self.osvs  = "7.1.1"
        self.mode  = self.MODE_FULL
        self.ftype = "Firmware"
        self.cltp  = 10
        self.cktp  = self.CKTP_CHECKMANUAL
        self.rtd   = self.RTD_UNROOTED
        self.chnl  = self.CHNL_WIFI
        self.timeout = 10
        self.reset_session()

    def reset_session(self):
        self.g2master = self.get_master_server()
        self.sess = requests.Session()
        if self.mode == self.MODE_FULL:
            self.sess.headers.update({"User-Agent": "com.tcl.fota/5.1.0.2.0029.0, Android"})
        else:
            self.sess.headers.update({"User-Agent": "tcl"})
        return self.sess

    @staticmethod
    def get_salt():
        millis = floor(time.time() * 1000)
        tail = "{:06d}".format(random.randint(0, 999999))
        return "{}{}".format(str(millis), tail)

    @staticmethod
    def get_master_server():
        master_servers = [
            "g2master-us-east.tclclouds.com",
            "g2master-us-west.tclclouds.com",
            "g2master-eu-west.tclclouds.com",
            "g2master-ap-south.tclclouds.com",
            "g2master-ap-north.tclclouds.com",
            "g2master-sa-east.tclclouds.com",
        ]
        return random.choice(master_servers)

    def do_check(self, https=True):
        protocol = "https://" if https else "http://"
        url = protocol + self.g2master + "/check.php"
        params = OrderedDict()
        params["id"]    = self.serid
        params["curef"] = self.curef
        params["fv"]    = self.fv
        params["mode"]  = self.mode
        params["type"]  = self.ftype
        params["cltp"]  = self.cltp
        params["cktp"]  = self.cktp
        params["rtd"]   = self.rtd
        params["chnl"]  = self.chnl
        #params["osvs"]  = self.osvs

        req = self.sess.get(url, params=params, timeout=self.timeout)
        if req.status_code == 200:
            return req.text
        elif req.status_code == 204:
            raise requests.exceptions.HTTPError("No update available.", response=req)
        elif req.status_code == 404:
            raise requests.exceptions.HTTPError("No data for requested CUREF/FV combination.", response=req)
        elif req.status_code in (500, 503):
            raise requests.exceptions.HTTPError("Server busy, try again later.", response=req)
        else:
            req.raise_for_status()
            raise requests.exceptions.HTTPError("HTTP {}.".format(req.status_code), response=req)

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
        params["mode"]  = self.mode
        params["vk"]    = self.get_vk2(params, self.cltp)
        params["cltp"]  = self.cltp
        params["cktp"]  = self.cktp
        params["rtd"]   = self.rtd
        if self.mode == self.MODE_FULL:
            params["foot"]  = 1
        params["chnl"]  = self.chnl

        #print(repr(dict(params)))
        req = self.sess.post(url, data=params)
        if req.status_code == 200:
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
