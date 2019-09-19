# -*- coding: utf-8 -*-


"""taptimise.taptimise: provides entry point main()."""

import argparse
import csv
import os
import io

import numpy as np
from pyfiglet import Figlet
from matplotlib import pyplot as plt

from .__init__ import __version__
from .optimise import optimise

WINDOW_SIZE = 11  # must be an odd number


def smooth(a, WSZ=WINDOW_SIZE):
    # a: NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    # as in the original MATLAB implementation
    if len(a) < WSZ:
        return a
    out0 = np.convolve(a, np.ones(WSZ, dtype=int), 'valid') / WSZ
    r = np.arange(1, WSZ - 1, 2)
    start = np.cumsum(a[:WSZ - 1])[::2] / r
    stop = (np.cumsum(a[:-WSZ:-1])[::2] / r)[::-1]
    return np.concatenate((start, out0, stop))


def main():
    custom_fig = Figlet(font='graffiti')
    print(custom_fig.renderText('Taptimise'))
    print('Tap placement optimiser with Monte-Carlo-Annealer')
    print('Copyright 2019 C. J. Williams (CHURCHILL COLLEGE)')
    print('This is free software with ABSOLUTELY NO WARRANTY')
    print()

    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="path to house data")
    parser.add_argument('max_load', type=float,
                        help="maximum load a single tap can support")
    parser.add_argument('-n', '--num-taps', type=int, action='store',
                        help="number of taps to start with")
    parser.add_argument("-m", "--max-distance", type=float, default=-1,
                        help="maximum house-tap distance", action="store")
    parser.add_argument('-b', '--buffer-size', type=int, action='store',
                        help='size of each houses internal buffer')
    parser.add_argument("-s", "--steps", action="store", type=int,
                        help="number of cooling steps per scale")
    parser.add_argument('--num-scales', action='store', type=int,
                        help='set number of scales')
    parser.add_argument('--disable-auto', action='store_true',
                        help='disables auto rerun if house too far')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='save run data for debugging')
    parser.add_argument("-v", "--version", action="store_true",
                        help="Show version and exit")

    args = parser.parse_args()

    if args.version:
        exit('Version: ' + __version__)

    if os.path.isabs(args.path):
        path = os.path.normpath(args.path)
    else:
        path = os.path.abspath(args.path)

    raw_houses = []

    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_houses.append([float(elem) for elem in row])

    max_dist = args.max_distance + 1
    num_taps = args.num_taps

    while max_dist > args.max_distance:
        houses, taps, max_dist, run_data = optimise(raw_houses, args.max_load,
                                                    num_taps=num_taps,
                                                    steps=args.steps,
                                                    debug=args.debug,
                                                    multiscale=args.num_scales,
                                                    max_dist=args.max_distance,
                                                    buff_size=args.buffer_size)
        num_taps = len(taps) + 1

        print()

        if args.disable_auto or args.max_distance < 0:
            break

    # visulise here

    # for h in houses:
    #     print(h)

    cmap = plt.cm.get_cmap('nipy_spectral', len(taps))

    h = np.asarray(houses)
    t = np.asarray(taps)

    f, a = plt.subplots()

    a.scatter(h[::, 1], h[::, 0], c=h[::, 2], cmap=cmap, label='Houses', s=16)
    a.plot(t[:, 1], t[:, 0], '+', color='k', markersize=8, label='Taps')
    a.set_title("Optimised for " + str(len(taps)) + ' taps')
    a.set_aspect('equal')

    a.set_ylabel('Latitude')
    a.set_xlabel('Longitude')

    xmin, xmax = h[::, 1].min(), h[::, 1].max()
    ymin, ymax = h[::, 0].min(), h[::, 0].max()

    gap = max(xmax - xmin, ymax - ymin)

    a.set_xlim((xmin, xmin + gap))
    a.set_ylim((ymin, ymin + gap))

    a.legend()

    dummy = io.BytesIO()
    f.savefig(dummy, format="svg")

    svg = '<svg' + str(dummy.getvalue()).split('<svg')[1]

    s1 = f'''
    <html>
    <head>
    <title>
    A Simple HTML Document
    </title>
    </head>
    <body>
    <p>This is a very simple HTML document</p>
    <p>It only has two paragraphs</p>
    {svg}
    </body>
    </html>'''

    with open(f"{os.path.basename(args.path)[:-4]}.html", "w") as html:
        print(s1, file=html)

    if args.debug:

        width = 1

        fig2, axis = plt.subplots(len(run_data))

        E0 = run_data[0][0][1]

        for ax, run in zip(axis, run_data):

            data = np.asarray(run)
            ind = np.arange(len(run))

            ax.set_xlabel('Monte-Carlo Steps')
            ax.set_ylabel('Counters')
            ax.plot(ind, smooth(data[::, 2]))
            ax.plot(ind, smooth(data[::, 3] + data[::, 2]))
            ax.plot(ind, smooth(data[::, 4] + data[::, 2] + data[::, 3]))
            ax.set_xlim(ind[0], ind[-1])
            ax.set_ylim(bottom=0)

            ax2 = ax.twinx()

            ax2.set_ylabel('Energy')
            ax2.plot(ind, smooth(data[::, 1] / E0), color='k')

        fig2.tight_layout()

        print('Percentage loads:', ', '.join(str(tap[3]) for tap in taps))

        print('Total final energy is: ', run_data[-1][-1][1])

    print('The biggest walk is:', max_dist)

    plt.show()
