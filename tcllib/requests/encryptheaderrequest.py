#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic encrypted header download request."""

from collections import OrderedDict

from .. import credentials
from .tclrequest import TclRequest
from .tclresult import EncryptHeaderResult


class EncryptHeaderRequest(TclRequest):
    """Generic encrypted header download request."""

    def __init__(self, file_uri):
        """Populate variables."""
        super().__init__()
        # NOTE: THIS HAS TO BE RUN ON AN ENCSLAVE
        self.uri = "/encrypt_header.php"
        self.rawmode = True
        self.method = "POST"
        self.file_uri = file_uri

    def get_headers(self):
        """Return request headers."""
        return {"User-Agent": "tcl"}

    def get_params(self):
        """Return request parameters."""
        params = OrderedDict()
        params.update(credentials.get_creds2())
        params["address"] = bytes(self.file_uri, "utf-8")
        return params

    def is_done(self, http_status: int, contents: str) -> bool:
        """Handle request result."""
        # Expect "HTTP 206 Partial Content" response
        if http_status == 206:
            self.result = EncryptHeaderResult(contents)
            self.success = True
            return True
        self.error = "HTTP {}".format(http_status)
        self.success = False
        return True
