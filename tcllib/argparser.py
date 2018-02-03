#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Custom argument parser."""

import argparse
import webbrowser


class DefaultParser(argparse.ArgumentParser):
    """argparse parser with some defaults set."""
    def __init__(self, appname, desc=None):
        """Set default name, description, epilogue, arguments."""
        homeurl = "https://github.com/mbirth/tcl_ota_check"
        super().__init__(prog=appname, description=desc, epilog=homeurl)
        self.add_argument("--webdb", help="open web database in browser and exit", action="store_true")

    def parse_args(self, args=None, namespace=None):
        """Parse special args first, defer to parent class second."""
        if set(args) & {"--webdb"}:  # if they intersect
            webbrowser.open("https://tclota.birth-online.de/", new=2)
            raise SystemExit
        else:
            argx = super().parse_args(args, namespace)
            return argx
