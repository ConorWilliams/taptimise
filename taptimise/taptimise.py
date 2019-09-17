# -*- coding: utf-8 -*-


"""taptimise.taptimise: provides entry point main()."""

import argparse
import csv
import os

from .__init__ import __version__
from .optimise import optimise


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("path", help="path to house data")

    parser.add_argument('max_load', type=float,
                        help="maximum load a single tap can support")

    parser.add_argument('-n', '--num-taps', type=int, action='store',
                        help="number of taps to start with")

    parser.add_argument("-m", "--max-distance", type=float, default=-1,
                        help="maximum house-tap distance", action="store")

    parser.add_argument('-d', '--debug', action='store_false',
                        help='save run data for debugging')

    parser.add_argument("-s", "--steps", action="store_true",
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

        houses, taps, max_dist, run_data = optimise(houses, num_taps, args.max_load,
                                                    steps=args.steps,
                                                    debug=args.debug,
                                                    multiscale=args.disable_multiscale,
                                                    max_dist=args.max_distance)

        num_taps = len(taps) + 1

        if args.disable_auto:
            break

    print(houses)

    print('Done')
