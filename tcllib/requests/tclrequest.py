#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic TCL request object."""

from . import tclresult


class TclRequest:
    """Generic TCL request object."""

    def __init__(self):
        """Populate variables."""
        self.uri = ""
        self.rawmode = False
        self.response = None
        self.result = None
        self.error = None
        self.success = False

    def get_headers(self):
        """Return request headers."""
        return {}

    def get_params(self):
        """Return request parameters."""
        return {}

    def is_done(self, http_status: int, contents: str):
        """Check if query is done or needs retry."""
        return False

    def get_result(self) -> tclresult.TclResult:
        """Return Result object."""
        return self.result
