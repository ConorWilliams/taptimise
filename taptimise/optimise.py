# -*- coding: utf-8 -*-

import random
import math
import statistics

from tqdm import trange, tqdm

from .classes import Tap, House

BUFFER_MULTIPLYER = 3
STEP_MULTIPLYER = 100
ZTC_MULTIPLYER = 1


KB_AVERAGE_RUNS = 100


def print_through(val):
    print(val)
    return val


def optimise(
    houses,
    max_load,
    num_taps=None,
    steps=None,
    debug=False,
    multiscale=None,
    max_dist=-1,
    buff_size=None,
    norelax=False,
):
    # finds optimal tap position for houses
    tot_demand = sum(h[2] for h in houses)

    if num_taps is None:
        num_taps = int(math.ceil(tot_demand / max_load))
    elif num_taps * max_load < tot_demand:
        print("WARNING - Not enough taps to support village")

    print("Attempting to optimise", num_taps, "taps.")

    avg_frac_load = tot_demand / (num_taps * max_load)

    if steps is None:
        steps = int(num_taps * STEP_MULTIPLYER)
    else:
        steps = int(num_taps * steps)

    ztc_steps = int(steps * ZTC_MULTIPLYER)

    print("Running,", steps / num_taps, "MCS per taps.")

    if buff_size is None:
        buff_size = num_taps * BUFFER_MULTIPLYER

    if max_dist < 0:
        max_sq_dist = -1
    else:
        max_sq_dist = max_dist ** 2

    # main object lists
    houses = [House(*h, buff_size, max_sq_dist) for h in houses]
    taps = [Tap(max_load * avg_frac_load) for _ in range(num_taps)]

    kB = 0
    # computes the expectation kB of a random (uncentalised) layout
    for _ in range(KB_AVERAGE_RUNS):
        randomise(houses, taps)
        kB += calc_kB(houses, taps)

    kB /= KB_AVERAGE_RUNS

    if multiscale is None:
        num_scales = calc_scales(houses)
    else:
        num_scales = multiscale

    print()
    print("Optimising over %d length scales:" % num_scales)
    # main cooling
    debug_data = []

    run_info = cool(houses, taps, steps, kB, num_scales, debug=debug)
    debug_data.append(run_info)

    # zero temp cooling
    print()
    print("Zero temperature & pair wise optimisations:")

    run_info = cool(houses, taps, ztc_steps, -1, 1, debug=debug)
    debug_data.append(run_info)

    if not norelax:
        print("Relaxed", relax(houses, taps), "pairs.")

    h_out = [
        [h.pos.real, h.pos.imag, find_tap_index(h, taps), h.dist(h.tap)]
        for h in houses
    ]

    t_out = [
        [t.pos.real, t.pos.imag, i, round(t.load)] for i, t in enumerate(taps)
    ]

    max_dist = max(out[3] for out in h_out)

    return (h_out, t_out, max_dist, debug_data, sum(t.energy for t in taps))


def cool(houses, taps, steps, kB, scales, debug=False):
    # performs a round of cooling to optimise tap positions
    energy = 0
    data = []

    for t in taps:
        t.centralise()
        t.score()
        energy += t.energy

    # one tap edge case
    if len(taps) <= 1:
        if debug:
            data.append([1, energy, 0, 0, 0])

        return data

    base = 10 ** -(2 / steps)  # 1 > temp_end > 0.01

    num_taps = len(taps)

    for scale in range(scales):
        temp = 1.0
        for i in trange(steps, ascii=True):
            temp = base * temp

            if debug:
                counters = [0, 0, 0]

            # for rejection sampling, does not matter that it is not updated every
            # house as worst case all taps become equally (un)likely
            emax = max(t.energy for t in taps)

            for _ in range(len(houses)):
                # rejection sampling to choose a house connected to a tap with a
                # probability proportional to the taps energy
                while True:
                    old_tap = taps[int(random.random() * num_taps)]
                    p = old_tap.energy / emax
                    rand = random.random()

                    if p >= 1 or rand < p:
                        # This is a bad way to extract a random element fom a set.
                        j = int(random.random() * len(old_tap.houses))
                        h = tuple(old_tap.houses)[j]
                        break
                    elif rand < 0.01:
                        # Hacky fix for large emax issues
                        emax = max(t.energy for t in taps)

                # picks a new tap from buffer i.e more likely to be a near by tap
                new_tap = h.buff.rand()

                # if new tap is current tap pick another tap using rejection
                # sampling such that probability of picking new tap is proportional
                # to 1 - tap.energy / emax
                while new_tap is old_tap:
                    for _ in range(num_taps):
                        new_tap = taps[int(random.random() * num_taps)]
                        p = new_tap.energy / emax
                        if (
                            p <= 0
                            or random.random() > p
                            or len(new_tap.houses) == 1
                        ):
                            break
                    else:  # nobreak
                        new_tap = random.choice(taps)

                # move house to new tap
                h.detach()
                h.attach(new_tap)

                old_tap.centralise()
                new_tap.centralise()

                delta_E = old_tap.score() + new_tap.score()

                if delta_E < 0:
                    # accept favourable move
                    if debug:
                        counters[0] += 1

                    energy += delta_E
                    h.buff.insert(new_tap)

                elif kB > 0 and random.random() < math.exp(
                    -delta_E / (kB * temp)
                ):
                    # accept unfavourable move
                    if debug:
                        counters[1] += 1

                    energy += delta_E
                    h.buff.insert(new_tap)

                else:
                    # reject unfavourable move
                    if debug:
                        counters[2] += 1

                    h.detach()
                    h.attach(old_tap)

                    old_tap.energy = old_tap.old_energy
                    new_tap.energy = new_tap.old_energy

                    old_tap.centralise()
                    new_tap.centralise()

                    h.buff.insert(old_tap)

            if debug:
                data.append([temp, energy, *counters])

        new_kB = calc_kB(houses, taps)
        if new_kB < kB:
            kB = new_kB
        elif scale != scales - 1:
            print("Stationary state detected - breaking loop early.")
            break

    else:  # nobreak
        if kB > 0:
            print("All length scales relaxed.")

    return data


def swap(h1, h2):
    # tries to swap the taps connected to h1 and h2. Returns the energy of the
    # swap and a boolean encoding if a swap occured.
    t1 = h1.tap
    t2 = h2.tap

    if t1 is t2:
        return 0, False

    h1.detach()
    h2.detach()

    h1.attach(t2)
    h2.attach(t1)

    return t1.score() + t2.score(), True


def relax(houses, taps):
    # Attempts to swap the taps connected to a pair of houses if the energy is
    # lowered does not affect tap positions
    random.shuffle(houses)
    swaps = 0
    avg = int(len(houses) / len(taps))

    tmp = sorted(houses, key=lambda x: houses[0].sqdist(x))

    for h in tqdm(tmp, ascii=True):
        houses.sort(key=lambda x: h.sqdist(x))
        near = houses[1 : avg + 1]

        for o in near:
            delta_E, swapped = swap(h, o)
            if delta_E > 0:
                swap(h, o)
            else:
                swaps += swapped

    return swaps


def randomise(houses, taps):
    # sets taps to random positions
    # assigns houses random tap
    # does not centralise taps

    xmin, xmax, ymin, ymax = get_grid(houses)

    for t in taps:
        t.pos = complex(random.uniform(xmin, xmax), random.uniform(ymin, ymax))

    for h in houses:
        if h.tap is not None:
            h.detach()

        tap = random.choice(taps)

        h.attach(tap)
        h.buff.insert(tap)

    return


def get_grid(houses):
    # returns a tuple of coordinates bounding houses in a square box

    x = [h.pos.real for h in houses]
    y = [h.pos.imag for h in houses]

    xmin, xmax = min(x), max(x)
    ymin, ymax = min(y), max(y)

    gap = max(xmax - xmin, ymax - ymin)

    return xmin, xmin + gap, ymin, ymin + gap


def calc_kB(houses, taps):
    # computes the median bond energy.
    # kB ~ average bond energy
    energy = []
    for tap in taps:
        tap.score()
        energy.append(tap.energy)

    return statistics.median(energy) * len(energy) / len(houses)


def calc_scales(houses):
    # finds the number of length scales in the village.
    dists = []
    for h in houses:
        for o in houses:
            if h is not o:
                rel = h.dist(o)
                if math.isclose(0, rel):
                    print("WARNING - two houses very close:", rel)
                else:
                    dists.append(rel)

    mind = min(dists)

    dists = [math.log10(d / mind) for d in dists]

    maxd = int(math.ceil(max(dists)))

    scales = [list() for _ in range(maxd)]

    for d in dists:
        scales[int(math.floor(d))].append(d)

    expectation = len(houses) - 1

    num_scales = 0
    for s in scales:
        if len(s) >= expectation:
            num_scales += 1

    if num_scales < 2:
        return 2
    else:
        return num_scales


def find_tap_index(house, taps):
    # finds index of house's tap in taps
    for c, tap in enumerate(taps):
        if tap is house.tap:
            return c
