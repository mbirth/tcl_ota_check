#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generic TCL API result handlers."""

import xml.dom.minidom

from defusedxml import ElementTree

from .. import dumpmgr


class TclResult:
    """Generic TCL API result."""

    def __init__(self, xmlstr: str):
        """Populate variables."""
        self.raw_xml = xmlstr
        self.dumper = dumpmgr.DumpMgr()
        self.dumper.write_dump(xmlstr)

    def delete_dump(self):
        """Delete last dump."""
        self.dumper.delete_last_dump()

    def pretty_xml(self):
        """Return prettified input XML with ``xml.dom.minidom``."""
        mdx = xml.dom.minidom.parseString(self.raw_xml)
        return mdx.toprettyxml(indent="  ")


class CheckResult(TclResult):
    """Handle check request result."""

    def __init__(self, xmlstr: str):
        """Extract data from check request result."""
        super().__init__(xmlstr)
        root = ElementTree.fromstring(xmlstr)
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
    """Handle download request result."""

    def __init__(self, xmlstr: str):
        """Extract data from download request result."""
        super().__init__(xmlstr)
        root = ElementTree.fromstring(xmlstr)
        file = root.find("FILE_LIST").find("FILE")
        self.fileid = file.find("FILE_ID").text
        self.fileurl = file.find("DOWNLOAD_URL").text
        s3_fileurl_node = file.find("S3_DOWNLOAD_URL")
        self.s3_fileurl = None
        if s3_fileurl_node is not None:
            self.s3_fileurl = s3_fileurl_node.text
        slave_list = root.find("SLAVE_LIST").findall("SLAVE")
        enc_list = root.find("SLAVE_LIST").findall("ENCRYPT_SLAVE")
        s3_slave_list = root.find("SLAVE_LIST").findall("S3_SLAVE")
        self.slaves = [s.text for s in slave_list]
        self.encslaves = [s.text for s in enc_list]
        self.s3_slaves = [s.text for s in s3_slave_list]


class ChecksumResult(TclResult):
    """Handle checksum request result."""

    def __init__(self, xmlstr: str):
        """Extract data from checksum request result."""
        super().__init__(xmlstr)
        root = ElementTree.fromstring(xmlstr)
        file = root.find("FILE_CHECKSUM_LIST").find("FILE")
        self.file_addr = file.find("ADDRESS").text
        self.sha1_enc_footer = file.find("ENCRYPT_FOOTER").text
        self.sha1_footer = file.find("FOOTER").text
        self.sha1_body = file.find("BODY").text


class EncryptHeaderResult(TclResult):
    """Handle encrypted header request result."""

    def __init__(self, contents: str):
        """Extract data from encrypted header request result."""
        self.rawdata = contents
