# -*- coding: utf-8 -*-

import requests
from collections import OrderedDict

class TimeoutException(Exception):
    pass

class HttpRequest:
    """Provides all generic features for making HTTP GET requests"""
    def __init__(self, url, timeout=10):
        self.url = url
        self.params = OrderedDict()
        self.timeout = timeout
        self.headers = {}

    def reset_session(self):
        """Reset everything to default."""
        self.sess = requests.Session()
        self.sess.headers.update(self.headers)

    def run(self):
        """Run query."""
        try:
            req = self.sess.get(self.url, params=self.params, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise TimeoutException(e)
        return req

class HttpPostRequest(HttpRequest):
    """Provides all generic features for making HTTP POST requests"""
    def run(self):
        """Run query."""
        try:
            req = self.sess.post(self.url, data=self.params, timeout=self.timeout)
        except requests.exceptions.Timeout as e:
            raise TimeoutException(e)
        return req
