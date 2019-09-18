# -*- coding: utf-8 -*-

import random
import math

from .classes import Tap, House

BUFFER_MULTIPLYER = 5
DEFAULT_NUM_SCALES = 2
STEP_MULTIPLYER = 100
KB_AVERAGE_RUNS = 1000
LENGTH_SCALE_THRESHOLD = 0.5


def optimise(houses, max_load, num_taps=None, steps=None, debug=False,
             multiscale=True, max_dist=-1, buff_size=None):
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

    # main object lists
    houses = [House(*h, buff_size, max_sq_dist) for h in houses]
    taps = [Tap(max_load, max_load * avg_frac_load) for _ in range(num_taps)]

    kB = 0
    for _ in range(KB_AVERAGE_RUNS):
        randomise(houses, taps)
        kB += calac_kB(houses, taps)

    kB /= KB_AVERAGE_RUNS

    if multiscale:
        num_scales = calc_scales(houses)
    else:
        num_scales = DEFAULT_NUM_SCALES

    print('Found %d length scales' % num_scales)

    # main cooling
    debug_data = []
    for _ in range(num_scales):
        run_info = cool(houses, taps, steps, kB, debug=debug)
        debug_data.append(run_info)

    # zero temp cooling
    run_info = cool(houses, taps, steps, kB, debug=debug)
    debug_data.append(run_info)

    h_out = [(h.pos.real, h.pos.imag, find_tap_index(h, taps), h.dist())
             for h in houses]
    t_out = [(t.pos.real, t.pos.imag, i, round(t.load / t.max_load))
             for i, t in enumerate(taps)]

    max_dist = max(out[3] for out in h_out)

    return h_out, t_out, max_dist, debug_data


def cool(houses, taps, steps, kB, debug=False):
    # performs a round of cooling to optimise tap positions
    return


def randomise(houses, taps):
    # sets taps to random positions
    # assigns houses random tap

    xmin, xmax, ymin, ymax = get_grid(houses)

    for t in taps:
        t.pos = complex(random.uniform(xmin, xmax), random.uniform(ymin, ymax))

    for h in houses:
        if h.tap is not None:
            h.detach()

        h.attach(random.choice(taps))

    return


def get_grid(houses):
    # returns a tuple of coordinates bounding houses in a square box
    x = [h.pos.real for h in houses]
    y = [h.pos.imag for h in houses]

    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    gap = max(xmax - xmin, ymax - ymin)

    return xmin, xmin + gap, ymin, ymin + gap


def calac_kB(houses, taps):
    # computes the expectation energy of current bonds
    energy = 0
    for tap in taps:
        tap.score()
        energy += tap.energy

    energy /= len(houses)

    return energy


def calc_scales(houses):
    # finds the number of length scales in the houses.
    dists = []
    for h in houses:
        for o in houses:
            if h is not o:
                rel = h.pos - o.pos
                rel = rel.real**2 + rel.imag**2
                if math.isclose(0, rel, rel_tol=1e-09, abs_tol=0.0):
                    print('WARNING - two houses very close')
                else:
                    dists.append(math.sqrt(rel))

    mind = min(dists)

    dists = [math.log10(d / mind) for d in dists]

    maxd = int(math.ceil(max(dists)))

    scales = [0 for _ in range(maxd)]

    for s in dists:
        scales[int(math.floor(s))] += 1

    expectation = len(dists) / maxd * LENGTH_SCALE_THRESHOLD

    num_scales = 0
    for s in scales:
        if s >= expectation:
            num_scales += 1

    # from matplotlib import pyplot as plt

    # plt.hist(dists, maxd)
    # plt.show()

    if num_scales < 2:
        return 2
    else:
        return num_scales


def find_tap_index(house, taps):
    # finds index of house's tap in taps
    for c, tap in enumerate(taps):
        if tap is house.tap:
            return c
