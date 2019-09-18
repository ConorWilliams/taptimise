# -*- coding: utf-8 -*-

import random
import math

from .classes import Tap, House

BUFFER_MULTIPLYER = 5
STEP_MULTIPLYER = 100


def optimise(houses, max_load, num_taps=None, steps=None, debug=False, multiscale=True, max_dist=-1, buff_size=None):
    # finds optimal tap position for houses

    print(max_load, num_taps, steps, debug, multiscale, max_dist, buff_size)

    tot_demand = sum(h[2] for h in houses)

    if num_taps is None:
        num_taps = int(math.ceil(tot_demand / max_load))

    avg_frac_load = tot_demand / (num_taps * max_load)

    if steps is None:
        steps = len(houses) * STEP_MULTIPLYER

    if buff_size is None:
        buff_size = num_taps * BUFFER_MULTIPLYER

    if max_dist < 0:
        max_sq_dist = -max_dist**2
    else:
        max_sq_dist = max_dist**2

    # build main data structures

    houses = [House(*h, buff_size, max_sq_dist) for h in houses]
    taps = [Tap(max_load, max_load * avg_frac_load) for _ in range(num_taps)]

    h_out, t_out, max_dist, debug_data = 1, [], 3, 4

    return h_out, t_out, max_dist, debug_data


def cool(*args):
    # performs a round of cooling to optimise tap positions
    return


def randomise(houses, taps):
    # sets taps to random positions
    # assigns houses random tap
    return


def get_grid(houses):
    # returns a tuple of coordinates bounding houses in a square box
    return 0, 0, 0, 0


def calac_kB(houses, taps):
    # computes the expectation energy of current bonds
    return


def calc_scales(houses):
    # finds the number of length scales in the houses.
    return 2


def find_tap(house, taps):
    # finds index of house's tap in taps
    return
