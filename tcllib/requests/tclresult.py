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

class DownloadResult(TclResult):
    def __init__(self, xml: str):
        super().__init__(xml)
        root = ElementTree.fromstring(xml)
        file = root.find("FILE_LIST").find("FILE")
        self.fileid = file.find("FILE_ID").text
        self.fileurl = file.find("DOWNLOAD_URL").text
        s3_fileurl_node = file.find("S3_DOWNLOAD_URL")
        self.s3_fileurl = None
        if s3_fileurl_node:
            self.s3_fileurl = s3_fileurl_node.text
        slave_list = root.find("SLAVE_LIST").findall("SLAVE")
        enc_list = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
        s3_slave_list = root.find("SLAVE_LIST").findall("S3_SLAVE")
        self.slaves = [s.text for s in slave_list]
        self.encslaves = [s.text for s in enc_list]
        self.s3_slaves = [s.text for s in s3_slave_list]
