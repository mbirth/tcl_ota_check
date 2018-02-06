#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Library for TCL API work and related functions."""

import enum

import requests

from . import (dumpmgr, servervote, tclcheck, tclchecksum, tclencheader,
               tclrequest)


def default_enum(enumname, vardict, qualroot="tcllib.FotaCheck"):
    """Enum with defaults set."""
    return enum.IntEnum(enumname, vardict, module=__name__, qualname="{}.{}".format(qualroot, enumname))


class FotaCheck(
        tclcheck.TclCheckMixin,
        tclrequest.TclRequestMixin,
        tclchecksum.TclChecksumMixin,
        tclencheader.TclEncHeaderMixin,
        servervote.ServerVoteMixin,
        dumpmgr.DumpMgrMixin
):
    """Main API handler class."""

    CKTP = default_enum("CKTP", ["AUTO", "MANUAL"])
    MODE = default_enum("MODE", {"OTA": 2, "FULL": 4})
    RTD = default_enum("RTD", ["UNROOTED", "ROOTED"])
    CHNL = default_enum("CHNL", ["3G", "WIFI"])
    CLTP = default_enum("CLTP", {"MOBILE": 10, "DESKTOP": 2010})
    CKOT = default_enum("CKOT", ["ALL", "AOTA_ONLY", "FOTA_ONLY"])

    def __init__(self):
        """Handle mixins and populate variables."""
        super().__init__()
        self.serid = "543212345000000"
        self.curef = "PRD-63117-011"
        self.fv = "AAM481"
        self.osvs = "7.1.1"
        self.mode = self.MODE.FULL
        self.ftype = "Firmware"
        self.cltp = self.CLTP.MOBILE
        self.cktp = self.CKTP.MANUAL
        self.ckot = self.CKOT.ALL
        self.rtd = self.RTD.UNROOTED
        self.chnl = self.CHNL.WIFI
        self.reset_session()

    def reset_session(self):
        """Reset everything to default."""
        self.g2master = self.get_master_server()
        self.sess = requests.Session()
        if self.mode == self.MODE.FULL:
            self.sess.headers.update({"User-Agent": "com.tcl.fota/5.1.0.2.0029.0, Android"})
        else:
            self.sess.headers.update({"User-Agent": "tcl"})
        return self.sess
