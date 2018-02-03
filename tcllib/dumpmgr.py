# -*- coding: utf-8 -*-

import errno
import glob
import os
from . import ansi

class DumpMgrMixin:
    def __init__(self):
        self.last_dump_filename = None

    def write_dump(self, data):
        outfile = os.path.normpath("logs/{}.xml".format(self.get_salt()))
        if not os.path.exists(os.path.dirname(outfile)):
            try:
                os.makedirs(os.path.dirname(outfile))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        with open(outfile, "w", encoding="utf-8") as f:
            f.write(data)
        self.last_dump_filename = outfile

    def delete_last_dump(self):
        if self.last_dump_filename:
            os.unlink(self.last_dump_filename)
            self.last_dump_filename = None

    @staticmethod
    def write_info_if_dumps_found():
        # To disable this info, uncomment the following line.
        #return
        files = glob.glob(os.path.normpath("logs/*.xml"))
        if len(files) > 0:
            print()
            print("{}There are {} logs collected in the logs/ directory.{} Please consider uploading".format(ansi.YELLOW, len(files), ansi.RESET))
            print("them to https://tclota.birth-online.de/ by running {}./upload_logs.py{}.".format(ansi.CYAN, ansi.RESET))
