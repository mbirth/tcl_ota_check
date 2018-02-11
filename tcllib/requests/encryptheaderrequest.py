# -*- coding: utf-8 -*-

from collections import OrderedDict
from .. import credentials, devices
from .tclrequest import TclRequest
from .tclresult import EncryptHeaderResult

class EncryptHeaderRequest(TclRequest):
    def __init__(self, file_uri):
        super().__init__()
        # NOTE: THIS HAS TO BE RUN ON AN ENCSLAVE
        self.uri = "/encrypt_header.php"
        self.rawmode = True
        self.method = "POST"
        self.file_uri = file_uri

    def get_headers(self):
        return {"User-Agent": "tcl"}

    def get_params(self):
        params = OrderedDict()
        params.update(credentials.get_creds2())
        params["address"] = bytes(self.file_uri, "utf-8")
        return params

    def is_done(self, http_status: int, contents: str) -> bool:
        # Expect "HTTP 206 Partial Content" response
        if http_status == 206:
            self.result = EncryptHeaderResult(contents)
            self.success = True
            return True
        self.error = "HTTP {}".format(http_status)
        self.success = False
        return True
