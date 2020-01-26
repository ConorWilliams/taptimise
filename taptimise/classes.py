# -*- coding: utf-8 -*-

import math
import random

BASE = 100
DISTANCE_EXPONENT = 2


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
    def __init__(self, exp_load):
        self.pos = complex(0, 0)
        self.vec_sum = complex(0, 0)

        self.energy = 0
        self.old_energy = 0

        self.load = 0
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
            sqdist = h.sqdist(self)

            # penalise bonds longer than max walking distance
            if h.max_sq_dist > 0 and sqdist > h.max_sq_dist:
                sqdist *= (sqdist / h.max_sq_dist) ** DISTANCE_EXPONENT

            self.energy += sqdist * h.demand

        self.energy *= BASE ** (
            ((self.load - self.exp_load) / self.exp_load) ** 2
        )

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
        return math.sqrt(self.sqdist(other))

    def sqdist(self, other):
        rel = self.pos - other.pos
        return rel.real ** 2 + rel.imag ** 2
