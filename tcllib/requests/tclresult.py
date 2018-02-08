# -*- coding: utf-8 -*-

from defusedxml import ElementTree


class TclResult:
    pass

class CheckResult(TclResult):
    def __init__(self, xml: str):
        self.raw_xml = xml
        root = ElementTree.fromstring(xml)
        self.curef = root.find("CUREF").text
        self.fvver = root.find("VERSION").find("FV").text
        self.tvver = root.find("VERSION").find("TV").text
        self.fw_id = root.find("FIRMWARE").find("FW_ID").text
        fileinfo = root.find("FIRMWARE").find("FILESET").find("FILE")
        self.fileid = fileinfo.find("FILE_ID").text
        self.filename = fileinfo.find("FILENAME").text
        self.filesize = fileinfo.find("SIZE").text
        self.filehash = fileinfo.find("CHECKSUM").text
