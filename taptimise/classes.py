# -*- coding: utf-8 -*-

import random

DISTANCE_PENALTY = 10
OVERLOAD_EXPONENT = 2


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

    def rand(self):
        return self.data[random.randint(0, len(self.data))]


class Tap():
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
        self.pos = self.vec_sum / self.load

    def score(self):
        self.old_energy = self.energy
        self.energy = 0

        for h in self.houses:
            self.energy += bond_energy(self, h)

        if self.load > self.max_load:
            energy *= (self.load / max_load) ** OVERLOAD_EXPONENT

        energy *= ((self.load / self.max_load - exp_load) / exp_load)**2


class House():
    def __init__(self, x, y, demand, buff_size, max_sq_dist):
        self.pos = complex(x, y)
        self.demand = demand
        self.tap = None
        self.buff = Buffer(buff_size)
        self.max_sq_dist = max_sq_dist

    def attach(self, tap):
        pass

    def detach(self):
        pass


def bond_energy(tap, house):
    rel = tap.pos - house.pos
    rel = rel.real**2 + rel.imag**2

    if rel > house.max_sq_dist:
        rel *= DISTANCE_PENALTY

    rel *= house.demand

    return rel
