# -*- coding: utf-8 -*-

import binascii
import hashlib
import random
import time
from math import floor
import zlib
from collections import OrderedDict
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

class TclRequest:
    @staticmethod
    def get_salt():
        millis = floor(time.time() * 1000)
        tail = "{:06d}".format(random.randint(0, 999999))
        return "{}{}".format(str(millis), tail)

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
