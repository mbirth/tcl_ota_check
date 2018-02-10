# -*- coding: utf-8 -*-

from .tclrequest import TclRequest
from . import http
from . import serverselector

class UnknownMethodException(Exception):
    pass

class RequestRunner:
    def __init__(self, server_selector: serverselector.ServerSelector, https=True):
        self.server_selector = server_selector
        self.protocol = "https://" if https else "http://"
        self.max_tries = 5

    def get_http(self, method="GET") -> http.HttpRequest:
        """Returns the http class according to desired method."""
        if method == "GET":
            return http.HttpRequest
        elif method == "POST":
            return http.HttpPostRequest
        raise UnknownMethodException("Unknown http method: {}".format(method))

    def get_server(self) -> str:
        """Returns a master server."""
        return self.server_selector.get_master_server()

    def run(self, query: TclRequest, timeout: int=10) -> bool:
        """Runs the actual query."""
        for _ in range(0, self.max_tries):
            url = "{}{}{}".format(self.protocol, self.get_server(), query.uri)
            http_handler = self.get_http(query.method)(url, timeout)
            http_handler.headers = query.get_headers()
            http_handler.params = query.get_params()
            http_handler.reset_session()
            self.server_selector.hook_prerequest()
            try:
                req = http_handler.run()
                req.encoding = "utf-8"
                done = query.is_done(req.status_code, req.text)
                self.server_selector.hook_postrequest(done)
                if done:
                    return done
            except http.TimeoutException:
                self.server_selector.hook_postrequest(False)
                query.error = "Timeout."
        query.error = "Max tries ({}) reached.".format(self.max_tries)
        return False
