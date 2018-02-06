#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to interface with TCL's download request API."""

import binascii
import hashlib
import random
import time
import zlib
from collections import OrderedDict
from math import floor

from defusedxml import ElementTree


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

VDKEY_B64Z = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"


def get_salt():
    """Generate cryptographic salt."""
    millis = floor(time.time() * 1000)
    tail = "{:06d}".format(random.randint(0, 999999))
    return "{}{}".format(str(millis), tail)


def get_vk2(params_dict, cltp):
    """Generate salted hash of API parameters."""
    params_dict["cltp"] = cltp
    query = ""
    for key, val in params_dict.items():
        if query:
            query += "&"
        query += key + "=" + str(val)
    vdk = zlib.decompress(binascii.a2b_base64(VDKEY_B64Z))
    query += vdk.decode("utf-8")
    engine = hashlib.sha1()
    engine.update(bytes(query, "utf-8"))
    hexhash = engine.hexdigest()
    return hexhash


class TclRequestMixin:
    """A mixin component for TCL's download request API."""

    def prep_request(self, curef, fvver, tvver, fw_id):
        """Prepare URL and device parameters for download request."""
        url = "https://" + self.g2master + "/download_request.php"
        params = OrderedDict()
        params["id"] = self.serid
        params["salt"] = get_salt()
        params["curef"] = curef
        params["fv"] = fvver
        params["tv"] = tvver
        params["type"] = self.ftype
        params["fw_id"] = fw_id
        params["mode"] = self.mode.value
        params["vk"] = get_vk2(params, self.cltp.value)
        params["cltp"] = self.cltp.value
        params["cktp"] = self.cktp.value
        params["rtd"] = self.rtd.value
        if self.mode == self.MODE.FULL:
            params["foot"] = 1
        params["chnl"] = self.chnl.value
        return url, params

    def do_request(self, curef, fvver, tvver, fw_id):
        """Perform download request with given parameters."""
        url, params = self.prep_request(curef, fvver, tvver, fw_id)
        # print(repr(dict(params)))
        req = self.sess.post(url, data=params)
        if req.status_code == 200:
            req.encoding = "utf-8"  # Force encoding as server doesn't give one
            self.write_dump(req.text)
            return req.text
        else:
            print("REQUEST: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit

    @staticmethod
    def parse_request(xmlstr):
        """Parse output of ``do_request``."""
        root = ElementTree.fromstring(xmlstr)
        file = root.find("FILE_LIST").find("FILE")
        fileid = file.find("FILE_ID").text
        fileurl = file.find("DOWNLOAD_URL").text
        s3_fileurl_node = file.find("S3_DOWNLOAD_URL")
        s3_fileurl = ""
        if s3_fileurl_node:
            s3_fileurl = s3_fileurl_node.text
        slave_list = root.find("SLAVE_LIST").findall("SLAVE")
        enc_list = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
        s3_slave_list = root.find("SLAVE_LIST").findall("S3_SLAVE")
        slaves = [s.text for s in slave_list]
        encslaves = [s.text for s in enc_list]
        s3_slaves = [s.text for s in s3_slave_list]
        return fileid, fileurl, slaves, encslaves, s3_fileurl, s3_slaves
