#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to manage dumps of API requests."""

import errno
import glob
import os
import random
import time
from math import floor

from . import ansi


def get_timestamp_random():
    """Generate timestamp + random part to avoid collisions."""
    millis = floor(time.time() * 1000)
    tail = "{:06d}".format(random.randint(0, 999999))
    return "{}_{}".format(str(millis), tail)

def write_info_if_dumps_found():
    """Notify user to upload dumps if present."""
    # To disable this info, uncomment the following line.
    # return
    files = glob.glob(os.path.normpath("logs/*.xml"))
    if files:
        print()
        print("{}There are {} logs collected in the logs/ directory.{} Please consider uploading".format(ansi.YELLOW, len(files), ansi.RESET))
        print("them to https://tclota.birth-online.de/ by running {}./upload_logs.py{}.".format(ansi.CYAN, ansi.RESET))

class DumpMgr:
    """A class for XML dump management."""

    def __init__(self):
        """Populate dump file name."""
        self.last_dump_filename = None

    def write_dump(self, data):
        """Write dump to file."""
        outfile = os.path.normpath("logs/{}.xml".format(get_timestamp_random()))
        if not os.path.exists(os.path.dirname(outfile)):
            try:
                os.makedirs(os.path.dirname(outfile))
            except OSError as err:
                if err.errno != errno.EEXIST:
                    raise
        with open(outfile, "w", encoding="utf-8") as fhandle:
            fhandle.write(data)
        self.last_dump_filename = outfile

    def delete_last_dump(self):
        """Delete last dump."""
        if self.last_dump_filename:
            os.unlink(self.last_dump_filename)
            self.last_dump_filename = None
