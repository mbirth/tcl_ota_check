#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pseudo-devices for desktop/mobile requests"""


class Device():
    """Generic pseudo-device class."""
    CLTP_STATES = {
        "MOBILE": 10,     # only show actual newer versions or HTTP 206
        "DESKTOP": 2010,  # always show latest version for FULL updates
    }
    MODE_STATES = {"OTA": 2, "FULL": 4}
    CHNL_STATES = {"3G": 1, "WIFI": 2}
    CKTP_STATES = {"AUTO": 1, "MANUAL": 2}
    CKOT_STATES = {"ALL": 1, "AOTA_ONLY": 2, "FOTA_ONLY": 3}

    def __init__(self, curef, fwver):
        """Populate variables."""
        self.curef = curef
        self.imei = ""
        self.osver = "7.1.1"
        self.fwver = fwver
        self.rtd = 0
        self.cltp = self.CLTP_STATES["DESKTOP"]
        self.mode = self.MODE_STATES["FULL"]
        self.type = "Firmware"
        self.chnl = self.CHNL_STATES["WIFI"]
        self.cktp = self.CKTP_STATES["MANUAL"]
        self.ckot = self.CKOT_STATES["ALL"]
        self.uagent = "tcl"

    def is_rooted(self):
        """Get RTD as boolean."""
        return self.rtd == 1

    def set_rooted(self, new_state: bool):
        """Set RTD as integer."""
        self.rtd = int(new_state)

    def set_cltp(self, new_cltp: str):
        """Set CLTP while handling non-numeric input."""
        # (Numerical CLTPs can be set by direct assigns.)
        # Throws exception when invalid cltp given:
        self.cltp = self.CLTP_STATES[new_cltp]

    def set_mode(self, new_mode: str):
        """Set MODE while handling non-numeric input."""
        # (Numerical MODEs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.mode = self.MODE_STATES[new_mode]

    def set_chnl(self, new_chnl: str):
        """Set CHNL while handling non-numeric input."""
        # (Numerical CHNLs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.chnl = self.CHNL_STATES[new_chnl]

    def set_ckot(self, new_ckot: str):
        """Set CKOT while handling non-numeric input."""
        # (Numerical CKOTs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.ckot = self.CKOT_STATES[new_ckot]


class MobileDevice(Device):
    """Generic mobile (i.e. OTA) device."""

    def __init__(self, curef="PRD-63117-011", fwver="AAO472"):
        """Populate variables."""
        super().__init__(curef, fwver)
        self.imei = "3531510"
        self.set_cltp("MOBILE")
        self.set_mode("OTA")
        self.uagent = "com.tcl.fota/5.1.0.2.0029.0, Android"


class DesktopDevice(Device):
    """Generic desktop (i.e. full) device."""

    def __init__(self, curef="PRD-63117-011", fwver="AAA000"):
        """Populate variables."""
        super().__init__(curef, fwver)
        self.imei = "543212345000000"
        self.set_cltp("DESKTOP")
        self.set_mode("FULL")
