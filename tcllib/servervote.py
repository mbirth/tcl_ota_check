#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=C0111,C0326,C0103

"""Tools to sort API servers to find the least awful one."""

import numpy


class ServerVoteMixin:
    """A mixin component for server sorting."""

    def __init__(self):
        """Populate server list and weighting variables."""
        self.g2master = None
        self.master_servers = [
            "g2master-us-east.tclclouds.com",
            "g2master-us-west.tclclouds.com",
            "g2master-eu-west.tclclouds.com",
            "g2master-ap-south.tclclouds.com",
            "g2master-ap-north.tclclouds.com",
            "g2master-sa-east.tclclouds.com",
        ]
        self.master_servers_weights = [3] * len(self.master_servers)
        self.check_time_sum = 3
        self.check_time_count = 1

    def get_master_server(self):
        """Return weighted choice from server list."""
        weight_sum = 0
        for i in self.master_servers_weights:
            weight_sum += i
        numpy_weights = []
        for i in self.master_servers_weights:
            numpy_weights.append(i/weight_sum)
        return numpy.random.choice(self.master_servers, p=numpy_weights)

    def master_server_downvote(self):
        """Decrease weight of a server."""
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] > 1:
            self.master_servers_weights[idx] -= 1

    def master_server_upvote(self):
        """Increase weight of a server."""
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] < 10:
            self.master_servers_weights[idx] += 1

    def check_time_add(self, duration):
        """Record connection time."""
        self.check_time_sum += duration
        self.check_time_count += 1

    def check_time_avg(self):
        """Return average connection time."""
        return self.check_time_sum / self.check_time_count

    def master_server_vote_on_time(self, last_duration, avg_duration):
        """Change weight of a server based on average connection time."""
        if last_duration < avg_duration - 0.5:
            self.master_server_upvote()
        elif last_duration > avg_duration + 0.5:
            self.master_server_downvote()
