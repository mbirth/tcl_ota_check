#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Library for TCL API work and related functions."""

import requests

from . import (dumpmgr, servervote, tclcheck, tclchecksum, tclencheader,
               tclrequest)


class FotaCheck(
        tclcheck.TclCheckMixin,
        tclrequest.TclRequestMixin,
        tclchecksum.TclChecksumMixin,
        tclencheader.TclEncHeaderMixin,
        servervote.ServerVoteMixin,
        dumpmgr.DumpMgrMixin
):
    """Main API handler class."""

    def __init__(self):
        """Handle mixins and populate variables."""
        super().__init__()
        self.reset_session()

    def reset_session(self, device=None):
        """Reset everything to default."""
        self.g2master = self.get_master_server()
        self.sess = requests.Session()
        if device:
            self.sess.headers.update({"User-Agent": device.ua})
        return self.sess
