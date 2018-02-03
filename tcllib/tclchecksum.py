#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

import json

from defusedxml import ElementTree


class TclChecksumMixin:
    def do_checksum(self, encslave, address, uri):
        url = "http://" + encslave + "/checksum.php"
        params = self.get_creds2()

        payload = {address: uri}
        payload_json = json.dumps(payload)
        params[b"address"] = bytes(payload_json, "utf-8")

        # print(repr(dict(params)))
        req = self.sess.post(url, data=params)
        if req.status_code == 200:
            req.encoding = "utf-8"  # Force encoding as server doesn't give one
            self.write_dump(req.text)
            # <ENCRYPT_FOOTER>2abfa6f6507044fec995efede5d818e62a0b19b5</ENCRYPT_FOOTER> means ERROR (invalid ADDRESS!)
            if "<ENCRYPT_FOOTER>2abfa6f6507044fec995efede5d818e62a0b19b5</ENCRYPT_FOOTER>" in req.text:
                print("INVALID URI: {}".format(uri))
                raise SystemExit
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
