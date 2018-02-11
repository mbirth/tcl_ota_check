#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic file checksum request."""

import json
from collections import OrderedDict

from .. import credentials
from .tclrequest import TclRequest
from .tclresult import ChecksumResult


class ChecksumRequest(TclRequest):
    """Generic file checksum request."""

    def __init__(self, address, file_uri):
        """Populate variables."""
        super().__init__()
        # NOTE: THIS HAS TO BE RUN ON AN ENCSLAVE
        self.uri = "/checksum.php"
        self.method = "POST"
        self.address = address
        self.file_uri = file_uri

    def get_headers(self):
        """Return request headers."""
        return {"User-Agent": "tcl"}

    def get_params(self):
        """Return request parameters."""
        params = OrderedDict()
        params.update(credentials.get_creds2())
        payload = {self.address: self.file_uri}
        payload_json = json.dumps(payload)
        params["address"] = bytes(payload_json, "utf-8")
        return params

    def is_done(self, http_status: int, contents: str) -> bool:
        """Handle request result."""
        if http_status == 200:
            # <ENCRYPT_FOOTER>2abfa6f6507044fec995efede5d818e62a0b19b5</ENCRYPT_FOOTER> means ERROR (invalid ADDRESS!)
            if "<ENCRYPT_FOOTER>2abfa6f6507044fec995efede5d818e62a0b19b5</ENCRYPT_FOOTER>" in contents:
                self.error = "INVALID URI: {}".format(self.file_uri)
                self.success = False
                return True
            self.response = contents
            self.result = ChecksumResult(contents)
            self.success = True
            return True
        self.error = "HTTP {}".format(http_status)
        self.success = False
        return True
