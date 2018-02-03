#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""XML tools."""

import xml.dom.minidom


class XmlToolsMixin:
    """A mixin component for XML tools."""
    @staticmethod
    def pretty_xml(xmlstr):
        """Prettify input XML with ``xml.dom.minidom``."""
        mdx = xml.dom.minidom.parseString(xmlstr)
        return mdx.toprettyxml(indent="  ")
