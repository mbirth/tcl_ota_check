#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to interface with TCL's encrypted header API."""


class TclEncHeaderMixin:
    """A mixin component for TCL's encrypted header API.."""
    def do_encrypt_header(self, encslave, address):
        """Perform encrypted header request with given parameters."""
        params = self.get_creds2()
        params[b"address"] = bytes(address, "utf-8")
        url = "http://" + encslave + "/encrypt_header.php"
        req = self.sess.post(url, data=params, verify=False)
        # Expect "HTTP 206 Partial Content" response
        if req.status_code == 206:
            return req.content
        else:
            print("ENCRYPT: " + repr(req))
            print(repr(req.headers))
            print(repr(req.text))
            raise SystemExit
