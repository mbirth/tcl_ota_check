#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to manage request authentication."""

import base64


def get_creds():
    """Return main authentication."""
    creds = {
        b"YWNjb3VudA==": b"emhlbmdodWEuZ2Fv",
        b"cGFzc3dvcmQ=": b"cWFydUQ0b2s=",
    }
    params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
    return params


def get_creds2():
    """Return alternate authentication."""
    creds = {
        b"YWNjb3VudA==": b"VGVsZUV4dFRlc3Q=",
        b"cGFzc3dvcmQ=": b"dDA1MjM=",
    }
    params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
    return params
