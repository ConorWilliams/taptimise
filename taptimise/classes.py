# -*- coding: utf-8 -*-

import math
import random

DISTANCE_EXPONENT = 1
OVERLOAD_EXPONENT = 2
OVERLOAD_BASE = 10
EXPECTATION_EXPONENT = 2


class Buffer():
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
        if self.load == 0:
            return
        self.pos = self.vec_sum / self.load

    def score(self):
        self.old_energy = self.energy
        self.energy = 0

        for h in self.houses:
            self.energy += bond_energy(self, h)

        # self.energy *= (1 + abs(self.load - self.exp_load) / self.exp_load)

        if self.load > self.exp_load:
            self.energy *= (self.load / self.exp_load) ** EXPECTATION_EXPONENT

        if self.load > self.max_load:
            self.energy *= (OVERLOAD_BASE ** (self.load / self.max_load - 1))

        return self.energy - self.old_energy


def bond_energy(tap, house):
    rel = tap.pos - house.pos
    rel = rel.real**2 + rel.imag**2

    if house.max_sq_dist > 0 and rel > house.max_sq_dist:
        rel *= ((rel / house.max_sq_dist) ** DISTANCE_EXPONENT)

    rel *= house.demand

    return rel


class House():
    def __init__(self, x, y, demand, buff_size, max_sq_dist):
        self.pos = complex(x, y)
        self.demand = demand
        self.tap = None
        self.buff = Buffer(buff_size)
        self.max_sq_dist = max_sq_dist

    def detach(self):
        if self.tap is not None:
            self.tap.houses.remove(self)
            self.tap.vec_sum -= self.pos * self.demand
            self.tap.load -= self.demand

            self.tap = None

    def attach(self, tap):
        tap.houses.add(self)
        tap.vec_sum += self.pos * self.demand
        tap.load += self.demand

        self.tap = tap

    def dist(self):
        rel = self.pos - self.tap.pos
        rel = rel.real**2 + rel.imag**2
        return math.sqrt(rel)
