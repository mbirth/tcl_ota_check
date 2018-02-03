# -*- coding: utf-8 -*-

import base64

class Credentials:
    @staticmethod
    def get_creds():
        creds = {
            b"YWNjb3VudA==": b"emhlbmdodWEuZ2Fv",
            b"cGFzc3dvcmQ=": b"cWFydUQ0b2s=",
        }
        params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
        return params

    @staticmethod
    def get_creds2():
        creds = {
            b"YWNjb3VudA==": b"VGVsZUV4dFRlc3Q=",
            b"cGFzc3dvcmQ=": b"dDA1MjM=",
        }
        params = {base64.b64decode(key): base64.b64decode(val) for key, val in creds.items()}
        return params
