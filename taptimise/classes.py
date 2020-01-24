# -*- coding: utf-8 -*-

import math
import random

DISTANCE_EXPONENT = 1
OVERLOAD_EXPONENT = 2
OVERLOAD_BASE = 10
EXPECTATION_EXPONENT = 2


class Buffer:
    # Basic circular buffer overwrites on wrap-around
    def __init__(self, size):
        self.size = size
        self.pos = 0
        self.data = []

    def insert(self, obj):
        if len(self.data) < self.size:
            self.pos += 1
            self.data.append(obj)
        else:
            if self.pos == self.size:
                self.pos = 0

            self.data[self.pos] = obj
            self.pos += 1

    def rand(self):
        return random.choice(self.data)

    def clear(self):
        self.pos = 0
        self.data = []


class Tap:
    def __init__(self, max_load, exp_load):
        self.pos = complex(0, 0)
        self.vec_sum = complex(0, 0)

        self.energy = 0
        self.old_energy = 0

        self.load = 0
        self.max_load = max_load
        self.exp_load = exp_load

        self.houses = set()

    def centralise(self):
        # set position to centroid
        if self.load == 0:
            pass
        else:
            self.pos = self.vec_sum / self.load

    def score(self):
        # updates the taps total energy and returns the energy change.
        self.old_energy = self.energy
        self.energy = 0

        # sums all bond-energies
        for h in self.houses:
            rel = h.pos - self.pos
            rel = rel.real ** 2 + rel.imag ** 2

            # penalise bonds longer than max walking distance
            if h.max_sq_dist > 0 and rel > h.max_sq_dist:
                rel *= (rel / h.max_sq_dist) ** DISTANCE_EXPONENT

            rel *= h.demand

            self.energy += rel

        # penalise loads greater than mean/expectation load
        if self.load > self.exp_load:
            self.energy *= (self.load / self.exp_load) ** EXPECTATION_EXPONENT

        # penalise loads over maximum load exponentially
        if self.load > self.max_load:
            self.energy *= OVERLOAD_BASE ** (self.load / self.max_load - 1)

        return self.energy - self.old_energy


class House:
    def __init__(self, x, y, demand, buff_size, max_sq_dist):
        self.pos = complex(x, y)
        self.demand = demand
        self.tap = None
        self.buff = Buffer(buff_size)
        self.max_sq_dist = max_sq_dist

    def detach(self):
        # remove all traces from tap connection and disconnect
        if self.tap is not None:
            self.tap.houses.remove(self)
            self.tap.vec_sum -= self.pos * self.demand
            self.tap.load -= self.demand

            self.tap = None

    def attach(self, tap):
        # attach to a new tap updating it
        if tap is None:
            return

        tap.houses.add(self)
        tap.vec_sum += self.pos * self.demand
        tap.load += self.demand

        self.tap = tap

    def dist(self, other):
        rel = self.pos - other.pos
        rel = rel.real ** 2 + rel.imag ** 2
        return math.sqrt(rel)

    def sqdist(self, other):
        rel = self.pos - other.pos
        rel = rel.real ** 2 + rel.imag ** 2
        return rel
