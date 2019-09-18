# -*- coding: utf-8 -*-


"""taptimise.taptimise: provides entry point main()."""

import argparse
import csv
import os
import numpy as np
from matplotlib import pyplot as plt

from .__init__ import __version__
from .optimise import optimise


def smooth(a, WSZ):
    # a: NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    # as in the original MATLAB implementation
    out0 = np.convolve(a, np.ones(WSZ, dtype=int), 'valid') / WSZ
    r = np.arange(1, WSZ - 1, 2)
    start = np.cumsum(a[:WSZ - 1])[::2] / r
    stop = (np.cumsum(a[:-WSZ:-1])[::2] / r)[::-1]
    return np.concatenate((start, out0, stop))


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="path to house data")

    parser.add_argument('max_load', type=float,
                        help="maximum load a single tap can support")

    parser.add_argument('-n', '--num-taps', type=int, action='store',
                        help="number of taps to start with")

    parser.add_argument("-m", "--max-distance", type=float, default=-1,
                        help="maximum house-tap distance", action="store")

    parser.add_argument('-d', '--debug', action='store_true',
                        help='save run data for debugging')

    parser.add_argument('-b', '--buffer-size', type=int, action='store',
                        help='size of each houses internal buffer')

    parser.add_argument("-s", "--steps", action="store", type=int,
                        help="number of cooling steps per scale")

    parser.add_argument('--disable-multiscale', action='store_false',
                        help='disables multiscale detection')

    parser.add_argument('--disable-auto', action='store_false',
                        help='disables auto rerun if house too far')

    parser.add_argument("-v", "--version", action="store_true",
                        help="Show version and exit")

    args = parser.parse_args()

    if args.version:
        exit('Version: ' + __version__)

    if os.path.isabs(args.path):
        path = os.path.normpath(args.path)
    else:
        path = os.path.abspath(args.path)

    houses = []

    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            houses.append([float(elem) for elem in row])

    max_dist = args.max_distance + 1
    num_taps = args.num_taps

    while max_dist > args.max_distance:

        houses, taps, max_dist, run_data = optimise(houses, args.max_load,
                                                    num_taps=num_taps,
                                                    steps=args.steps,
                                                    debug=args.debug,
                                                    multiscale=args.disable_multiscale,
                                                    max_dist=args.max_distance,
                                                    buff_size=args.buffer_size)

        num_taps = len(taps) + 1

        if args.disable_auto:
            break

    # visulise here

    # for h in houses:
    #     print(h)

    cmap = plt.cm.get_cmap('nipy_spectral', len(taps))

    h = np.asarray(houses)
    t = np.asarray(taps)

    plt.scatter(h[::, 1], h[::, 0], c=h[::, 2], cmap=cmap, label='Houses', s=16)
    plt.plot(t[:, 1], t[:, 0], '+', color='k', markersize=8, label='Taps')
    plt.title("Optimised for " + str(len(taps)) + ' taps')
    plt.gca().set_aspect('equal')

    plt.xlabel('Latitude')
    plt.ylabel('Longitude')

    xmin, xmax = h[::, 1].min(), h[::, 1].max()
    ymin, ymax = h[::, 0].min(), h[::, 0].max()

    gap = max(xmax - xmin, ymax - ymin)

    plt.axis((xmin, xmin + gap, ymin, ymin + gap))

    plt.legend()

    if args.debug:

        width = 1       # the width of the bars: can also be len(x) sequence

        fig, axis = plt.subplots(len(run_data))

        window = 11

        E0 = run_data[0][0][1]

        for ax, run in zip(axis, run_data):

            data = np.asarray(run)
            ind = np.arange(data.shape[0])    # the x locations for the groups

            ax.set_xlabel('Monte-Carlo Steps')
            ax.set_ylabel('Counters')
            ax.plot(ind, smooth(data[::, 2], window))
            ax.plot(ind, smooth(data[::, 3] + data[::, 2], window))
            ax.plot(ind, smooth(data[::, 4] +
                                data[::, 2] + data[::, 3], window))

            ax2 = ax.twinx()  # instantiate a second axes that shares the same x-axis

            ax2.set_ylabel('Energy')
            ax2.plot(ind, smooth(data[::, 1] / E0, window), color='k')

            fig.tight_layout()  # otherwise the right y-label is slightly clipped

    for tap in taps:
        print(tap[3])

    plt.show()
