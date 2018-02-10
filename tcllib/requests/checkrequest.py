# -*- coding: utf-8 -*-

from collections import OrderedDict
from .. import devices
from .tclrequest import TclRequest
from .tclresult import CheckResult

class CheckRequest(TclRequest):
    def __init__(self, device: devices.Device):
        super().__init__()
        self.uri = "/check.php"
        self.method = "GET"
        self.device = device
    
    def get_headers(self):
        return {"User-Agent": self.device.ua}

    def get_params(self):
        params = OrderedDict()
        params["id"] = self.device.imei
        params["curef"] = self.device.curef
        params["fv"] = self.device.fwver
        params["mode"] = self.device.mode
        params["type"] = self.device.type
        params["cltp"] = self.device.cltp
        params["cktp"] = self.device.cktp
        params["rtd"] = self.device.rtd
        params["chnl"] = self.device.chnl
        #params["osvs"] = self.device.osvs
        #params["ckot"] = self.device.ckot
        return params

    def is_done(self, http_status: int, contents: str) -> bool:
        ok_states = {
            204: "No update available.",
            404: "No data for requested CUREF/FV combination.",
        }
        if http_status == 200:
            self.response = contents
            self.result = CheckResult(contents)
            self.success = True
            return True
        elif http_status in ok_states:
            self.error = ok_states[http_status]
            self.success = False
            return True
        elif http_status not in [500, 502, 503]:
            # Errors OTHER than 500, 502 or 503 are probably
            # errors where we don't need to retry
            self.error ="HTTP {}.".format(http_status)
            self.success = False
            return True
        return False

# Check requests have 4 possible outcomes:
# 1. HTTP 200 with XML data - our desired info
# 2. HTTP 204 - means: no newer update available
# 3. HTTP 404 - means: invalid device or firmware version
# 4. anything else: server problem (esp. 500, 502, 503)
