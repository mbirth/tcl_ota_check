# -*- coding: utf-8 -*-

import xml.dom.minidom


class XmlToolsMixin:
    @staticmethod
    def pretty_xml(xmlstr):
        mdx = xml.dom.minidom.parseString(xmlstr)
        return mdx.toprettyxml(indent="  ")
