# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326

import argparse
import webbrowser


class DefaultParser(argparse.ArgumentParser):
    def __init__(self, appname, desc=None):
        super().__init__(prog=appname, description=desc, epilog="https://github.com/mbirth/tcl_ota_check")
        self.add_argument("--webdb", help="open web database in browser and exit", action="store_true")

    def parse_args(self, args=None, namespace=None):
        if set(args) & {"--webdb"}:  # if they intersect
            webbrowser.open("https://tclota.birth-online.de/", new=2)
            raise SystemExit
        else:
            argx = super().parse_args(args, namespace)
            return argx
