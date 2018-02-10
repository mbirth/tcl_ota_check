# -*- coding: utf-8 -*-

import xml.dom.minidom

from defusedxml import ElementTree

from . import dumpmgr


class TclResult:
    def __init__(self, xml: str):
        self.raw_xml = xml
        self.dumper = dumpmgr.DumpMgr()
        self.dumper.write_dump(xml)

    def delete_dump(self):
        self.dumper.delete_last_dump()

    def pretty_xml(self):
        """Return prettified input XML with ``xml.dom.minidom``."""
        mdx = xml.dom.minidom.parseString(self.raw_xml)
        return mdx.toprettyxml(indent="  ")

class CheckResult(TclResult):
    def __init__(self, xml: str):
        super().__init__(xml)
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
