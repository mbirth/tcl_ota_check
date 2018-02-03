# -*- coding: utf-8 -*-

import numpy

class ServerVote:
    def get_master_server(self):
        weight_sum = 0
        for i in self.master_servers_weights:
            weight_sum += i
        numpy_weights = []
        for i in self.master_servers_weights:
            numpy_weights.append(i/weight_sum)
        return numpy.random.choice(self.master_servers, p=numpy_weights)

    def master_server_downvote(self):
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] > 1:
            self.master_servers_weights[idx] -= 1

    def master_server_upvote(self):
        idx = self.master_servers.index(self.g2master)
        if self.master_servers_weights[idx] < 10:
            self.master_servers_weights[idx] += 1

    def check_time_add(self, duration):
        self.check_time_sum += duration
        self.check_time_count += 1

    def check_time_avg(self):
        return (self.check_time_sum / self.check_time_count)

    def master_server_vote_on_time(self, last_duration, avg_duration):
        if last_duration < avg_duration - 0.5:
            self.master_server_upvote()
        elif last_duration > avg_duration + 0.5:
            self.master_server_downvote()
