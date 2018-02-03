# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import enum
import requests
from . import credentials
from . import devlist
from . import dumpmgr
from . import servervote
from . import tclcheck
from . import tclrequest
from . import tclchecksum
from . import tclencheader
from . import xmltools

def default_enum(enumname, vardict):
    return enum.IntEnum(enumname, vardict, module=__name__, qualname="tcllib.FotaCheck.{}".format(enumname))

class FotaCheck(
    tclcheck.TclCheck,
    tclrequest.TclRequest,
    tclchecksum.TclChecksum,
    tclencheader.TclEncHeader,
    servervote.ServerVote,
    credentials.Credentials,
    devlist.DevList,
    dumpmgr.DumpMgr,
    xmltools.XmlTools
    ):
    VDKEY = b"eJwdjwEOwDAIAr8kKFr//7HhmqXp8AIIDrYAgg8byiUXrwRJRXja+d6iNxu0AhUooDCN9rd6rDLxmGIakUVWo3IGCTRWqCAt6X4jGEIUAxgN0eYWnp+LkpHQAg/PsO90ELsy0Npm/n2HbtPndFgGEV31R9OmT4O4nrddjc3Qt6nWscx7e+WRHq5UnOudtjw5skuV09pFhvmqnOEIs4ljPeel1wfLYUF4\n"
    CKTP = default_enum("CKTP", ["AUTO", "MANUAL"])
    MODE = default_enum("MODE", {"OTA": 2, "FULL": 4})
    RTD = default_enum("RTD", ["UNROOTED", "ROOTED"])
    CHNL = default_enum("CHNL", ["3G", "WIFI"])
    CLTP = default_enum("CLTP", {"MOBILE": 10, "DESKTOP": 2010})
    CKOT = default_enum("CKOT", ["ALL", "AOTA_ONLY", "FOTA_ONLY"])

    def __init__(self):
        self.serid = "543212345000000"
        self.curef = "PRD-63117-011"
        self.fv    = "AAM481"
        self.osvs  = "7.1.1"
        self.mode  = self.MODE.FULL
        self.ftype = "Firmware"
        self.cltp  = self.CLTP.MOBILE
        self.cktp  = self.CKTP.MANUAL
        self.ckot  = self.CKOT.ALL
        self.rtd   = self.RTD.UNROOTED
        self.chnl  = self.CHNL.WIFI
        self.g2master = None
        self.master_servers = [
            "g2master-us-east.tclclouds.com",
            "g2master-us-west.tclclouds.com",
            "g2master-eu-west.tclclouds.com",
            "g2master-ap-south.tclclouds.com",
            "g2master-ap-north.tclclouds.com",
            "g2master-sa-east.tclclouds.com",
        ]
        self.master_servers_weights = [3] * len(self.master_servers)
        self.check_time_sum = 3
        self.check_time_count = 1
        self.last_dump_filename = None
        self.reset_session()

    def reset_session(self):
        self.g2master = self.get_master_server()
        self.sess = requests.Session()
        if self.mode == self.MODE.FULL:
            self.sess.headers.update({"User-Agent": "com.tcl.fota/5.1.0.2.0029.0, Android"})
        else:
            self.sess.headers.update({"User-Agent": "tcl"})
        return self.sess
