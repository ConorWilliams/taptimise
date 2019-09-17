# -*- coding: utf-8 -*-

import random


class Buffer():
    def __init__(self, size):
        self.size = size
        self.pos = 0
        self.data = []

    def insert(self, obj):
        if len(self.data) < self.size:
            pos += 1
            self.data.append(obj)
        else:
            if pos == size:
                pos = 0

            self.data[pos] = obj
            pos += 1

    def rand(self)
        return self.data[random.randint(0, len(self.data))]


class Tap():
    def __init__(self):
        pass

    def centralise(self):
        pass

    def score(self):
        pass


class House():
    def __init__(self, x, y, demand, buff_size):
        self.pos = complex(x, y)
        self.demand = demand
        self.tap = None
        self.buff = Buffer(buff_size)

    def attach(self, tap):
        pass

    def detach(self)
        pass
