#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic file download request."""

import binascii
import hashlib
import random
import time
import zlib
from collections import OrderedDict
from math import floor

from .. import devices
from .tclrequest import TclRequest
from .tclresult import DownloadResult


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


class DownloadRequest(TclRequest):
    """Generic file download request."""

    def __init__(self, device: devices.Device, tvver: str, fw_id: str):
        """Populate variables."""
        super().__init__()
        self.uri = "/download_request.php"
        self.method = "POST"
        self.device = device
        self.tvver = tvver
        self.fw_id = fw_id

    def get_headers(self):
        """Return request headers."""
        return {"User-Agent": self.device.uagent}

    def get_params(self):
        """Return request parameters."""
        params = OrderedDict()
        params["id"] = self.device.imei
        params["salt"] = get_salt()
        params["curef"] = self.device.curef
        params["fv"] = self.device.fwver
        params["tv"] = self.tvver
        params["type"] = self.device.type
        params["fw_id"] = self.fw_id
        params["mode"] = self.device.mode
        params["vk"] = get_vk2(params, self.device.cltp)
        params["cltp"] = self.device.cltp
        params["cktp"] = self.device.cktp
        params["rtd"] = self.device.rtd
        if self.device.mode == self.device.MODE_STATES["FULL"]:
            params["foot"] = 1
        params["chnl"] = self.device.chnl
        return params

    def is_done(self, http_status: int, contents: str) -> bool:
        """Handle request result."""
        if http_status == 200:
            self.response = contents
            self.result = DownloadResult(contents)
            self.success = True
            return True
        elif http_status not in [500, 502, 503]:
            # Errors OTHER than 500, 502 or 503 are probably
            # errors where we don't need to retry
            self.error = "HTTP {}".format(http_status)
            self.success = False
            return True
        return False
