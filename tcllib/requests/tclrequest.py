# -*- coding: utf-8 -*-

from . import tclresult

class TclRequest:
    def __init__(self):
        self.uri = ""
        self.response = None
        self.result = None
        self.error = None
        self.success = False

    def get_headers(self):
        return {}

    def get_params(self):
        return {}

    def is_done(self, http_status: int, contents: str):
        """Checks if query is done or needs retry."""
        return False

    def get_result(self) -> tclresult.TclResult:
        """Returns Result object."""
        return self.result
