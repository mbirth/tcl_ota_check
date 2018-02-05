# -*- coding: utf-8 -*-

"""Pseudo-devices for desktop/mobile requests"""

class Device():
    CLTP_STATES = {
        "MOBILE": 10,     # only show actual newer versions or HTTP 206
        "DESKTOP": 2010,  # always show latest version for FULL updates
    }
    MODE_STATES = {"OTA": 2, "FULL": 4}
    CHNL_STATES = {"3G": 1, "WIFI": 2}
    CKTP_STATES = {"AUTO": 1, "MANUAL": 2}
    CKOT_STATES = {"ALL": 1, "AOTA_ONLY": 2, "FOTA_ONLY": 3}

    def __init__(self, curef, fwver):
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
        self.ua = "tcl"

    def is_rooted(self):
        return (self.rtd == 1)

    def set_rooted(self, new_state: bool):
        if new_state:
            self.rtd = 1
        else:
            self.rtd = 0

    def set_cltp(self, new_cltp: str):
        # (Numerical CLTPs can be set by direct assigns.)
        # Throws exception when invalid cltp given:
        self.cltp = self.CLTP_STATES[new_cltp]

    def set_mode(self, new_mode: str):
        # (Numerical MODEs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.mode = self.MODE_STATES[new_mode]

    def set_chnl(self, new_chnl: str):
        # (Numerical CHNLs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.chnl = self.CHNL_STATES[new_chnl]

    def set_ckot(self, new_ckot: str):
        # (Numerical CKOTs can be set by direct assigns.)
        # Throws exception when invalid mode given:
        self.ckot = self.CKOT_STATES[new_ckot]

class MobileDevice(Device):
    def __init__(self, curef="PRD-63117-011", fwver="AAO472"):
        super().__init__(curef, fwver)
        self.imei = "3531510"
        self.set_cltp("MOBILE")
        self.set_mode("OTA")
        self.ua = "com.tcl.fota/5.1.0.2.0029.0, Android"

class DesktopDevice(Device):
    def __init__(self, curef="PRD-63117-011", fwver="AAA000"):
        super().__init__(curef, fwver)
        self.imei = "543212345000000"
        self.set_cltp("DESKTOP")
        self.set_mode("FULL")
