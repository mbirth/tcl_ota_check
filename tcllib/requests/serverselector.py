# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to sort API servers to find the least awful one."""

import numpy
import time


MASTER_SERVERS = [
    "g2master-us-east.tclclouds.com",
    "g2master-us-west.tclclouds.com",
    "g2master-eu-west.tclclouds.com",
    "g2master-ap-south.tclclouds.com",
    "g2master-ap-north.tclclouds.com",
    "g2master-sa-east.tclclouds.com",
]

class ServerSelector:
    """Returns a random server to use."""

    def __init__(self, server_list=None):
        """Init stuff"""
        if server_list:
            self.server_list = server_list
        else:
            self.server_list = MASTER_SERVERS
        self.last_server = None

    def get_master_server(self):
        """Return a random server."""
        while True:
            new_server = numpy.random.choice(self.server_list)
            if new_server != self.last_server:
                break
        self.last_server = new_server
        return new_server

    def hook_prerequest(self):
        """Hook to be called before doing request"""
        pass

    def hook_postrequest(self, successful: bool):
        """Hook to be called after request finished"""
        pass

class ServerVoteSelector(ServerSelector):
    """Tries to return faster servers more often."""

    def __init__(self, server_list=None):
        """Populate server list and weighting variables."""
        super().__init__(server_list)
        self.servers_weights = [3] * len(self.server_list)
        self.check_time_sum = 3
        self.check_time_count = 1

    def get_master_server(self):
        """Return weighted choice from server list."""
        weight_sum = 0
        for i in self.servers_weights:
            weight_sum += i
        numpy_weights = []
        for i in self.servers_weights:
            numpy_weights.append(i/weight_sum)
        self.last_server = numpy.random.choice(self.server_list, p=numpy_weights)
        return self.last_server

    def master_server_downvote(self):
        """Decrease weight of last chosen server."""
        idx = self.server_list.index(self.last_server)
        if self.servers_weights[idx] > 1:
            self.servers_weights[idx] -= 1

    def master_server_upvote(self):
        """Increase weight of last chosen server."""
        idx = self.server_list.index(self.last_server)
        if self.servers_weights[idx] < 10:
            self.servers_weights[idx] += 1

    def check_time_add(self, duration):
        """Record connection time."""
        self.check_time_sum += duration
        self.check_time_count += 1

    def check_time_avg(self):
        """Return average connection time."""
        return self.check_time_sum / self.check_time_count

    def master_server_vote_on_time(self, last_duration):
        """Change weight of a server based on average connection time."""
        avg_duration = self.check_time_avg()
        if last_duration < avg_duration - 0.5:
            self.master_server_upvote()
        elif last_duration > avg_duration + 0.5:
            self.master_server_downvote()

    def hook_prerequest(self):
        """Hook to be called before doing request"""
        self.reqtime_start = time.perf_counter()

    def hook_postrequest(self, successful: bool):
        """Hook to be called after request finished"""
        reqtime = time.perf_counter() - self.reqtime_start
        self.check_time_add(reqtime)
        if successful:
            self.master_server_vote_on_time(reqtime)
        else:
            self.master_server_downvote()
