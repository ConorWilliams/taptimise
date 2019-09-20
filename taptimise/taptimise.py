# -*- coding: utf-8 -*-

"""taptimise.taptimise: provides entry point main()."""

import argparse
import csv
import os
import io
import sys

import numpy as np
from pyfiglet import Figlet
from matplotlib import pyplot as plt

from .__init__ import __version__
from .optimise import optimise
from .htmltable import to_html

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


def save_svg(fig):
    w, h = fig.get_size_inches()
    w, h = round(w + 0.5), round(h + 0.5)

    fig.set_size_inches(w, h)

    w, h = int(72 * w), int(72 * h)

    tmp = io.StringIO()
    fig.savefig(tmp, format="svg")

    svg = '<svg' + tmp.getvalue().split('<svg')[1]

    svg = svg.replace(f'height="{h}pt"', '', 1)
    svg = svg.replace(f'width="{w}pt"', 'width="100%"', 1)

    return svg


def formatter(prog):
    return argparse.HelpFormatter(prog, max_help_position=52)


def main():
    custom_fig = Figlet(font='graffiti')
    print(custom_fig.renderText('Taptimise'))
    print('Tap placement optimiser with Monte-Carlo-Annealer')
    print('Copyright 2019 C. J. Williams (CHURCHILL COLLEGE)')
    print('This is free software with ABSOLUTELY NO WARRANTY')
    print()

# ****************************************************************************
# *                              Parse Arguments                             *
# ****************************************************************************

    parser = argparse.ArgumentParser(formatter_class=formatter)

    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s ' + __version__)

    parser.add_argument("path", help="path to house data")
    parser.add_argument('max_load', type=float,
                        help="maximum load a single tap can support")

    parser.add_argument('-n', '--num-taps', type=int, action='store',
                        help="number of taps to start with",
                        metavar='NUM')
    parser.add_argument("-m", "--max-distance", type=float, default=-1,
                        help="maximum house-tap distance", action="store",
                        metavar='DIST')
    parser.add_argument('-b', '--buffer-size', type=int, action='store',
                        help='size of each houses internal buffer',
                        metavar='SIZE')
    parser.add_argument("-s", "--steps", action="store", type=int,
                        help="number of cooling steps per scale")
    parser.add_argument('--num-scales', action='store', type=int,
                        help='set number of scales')
    parser.add_argument('-o', '--overload', action='store', type=float,
                        help='Set the teleport overload threshold')

    parser.add_argument('--disable-auto', action='store_true',
                        help='disables auto rerun if house too far')
    parser.add_argument('--disable-debug', action='store_false',
                        help='save run data for debugging')

    args = parser.parse_args()

    if os.path.isabs(args.path):
        path = os.path.normpath(args.path)
    else:
        path = os.path.abspath(args.path)

# ****************************************************************************
# *                             Run Optimisation                             *
# ****************************************************************************

    raw_houses = []

    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            raw_houses.append([float(elem) for elem in row])

    max_dist = args.max_distance + 1
    num_taps = args.num_taps

    while max_dist > args.max_distance:
        houses, taps, max_dist, run_data, scales = optimise(raw_houses, args.max_load,
                                                            num_taps=num_taps,
                                                            steps=args.steps,
                                                            debug=args.disable_debug,
                                                            multiscale=args.num_scales,
                                                            max_dist=args.max_distance,
                                                            buff_size=args.buffer_size,
                                                            overvolt=args.overload)
        num_taps = len(taps) + 1

        print()

        if args.disable_auto or args.max_distance < 0:
            break

# ****************************************************************************
# *                               Plot Village                               *
# ****************************************************************************

    name = os.path.basename(args.path)[:-4]

    cmap = plt.cm.get_cmap('nipy_spectral', len(taps))

    h = np.asarray(houses)
    t = np.asarray(taps)

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter(h[::, 1], h[::, 0], c=h[::, 2], cmap=cmap, label='Houses', s=16)
    ax.plot(t[:, 1], t[:, 0], '+', color='k', markersize=8, label='Taps')
    ax.set_title(f"{name} optimised for " + str(len(taps)) + ' taps')
    ax.set_aspect('equal')

    ax.set_ylabel('Latitude')
    ax.set_xlabel('Longitude')

    xmin, xmax = h[::, 1].min(), h[::, 1].max()
    ymin, ymax = h[::, 0].min(), h[::, 0].max()

    gap = max(xmax - xmin, ymax - ymin)

    ax.set_xlim((xmin, xmin + gap))
    ax.set_ylim((ymin, ymin + gap))

    ax.xaxis.set_ticklabels([])
    ax.yaxis.set_ticklabels([])

    ax.set_xticks([])
    ax.set_yticks([])

    ax.legend()

    fig.tight_layout()

    map_svg = save_svg(fig)


# ****************************************************************************
# *                                Plot Debug                                *
# ****************************************************************************

    debug_svg = []

    if args.disable_debug:

        width = 1

        E0 = run_data[0][0][1]

        for order, run in enumerate(run_data):

            if order == len(run_data) - 1:
                order = "ZTC"

            fig, ax = plt.subplots()

            data = np.asarray(run)
            ind = np.arange(len(run))

            data[::, 2:5:1] *= 100 / len(houses)

            ax.set_xlabel('Monte-Carlo Steps')
            ax.set_ylabel('Percentage Count')
            ax.set_title(f'Order = {order}')

            ax.plot(ind, smooth(data[::, 2]), label='favourable')
            ax.plot(ind, smooth(data[::, 3] + data[::, 2]),
                    label='unfavourable-accepted')
            ax.plot(ind, data[::, 4] + data[::, 2] +
                    data[::, 3], label='unfavourable-rejected')

            ax.set_xlim(ind[0], ind[-1])
            ax.set_ylim(bottom=0)
            ax.legend()

            ax2 = ax.twinx()

            ax2.set_ylabel('Energy Fraction')
            ax2.plot(ind, smooth(data[::, 1] / E0), color='k')

            fig.tight_layout()

            svg = save_svg(fig)

            debug_svg.append(svg)

        print('Total final energy is: ', run_data[-1][-1][1])

    print('The biggest walk is:', max_dist)
    print('Percentage loads:', ', '.join(str(tap[3]) for tap in taps))

# ****************************************************************************
# *                                 Make html                                *
# ****************************************************************************
    percentage = 65
    raw_html = f'''
    <!DOCTYPE html>
    <html>

    <head>
    <title> Taptimise {name} Report </title>
    </head>

    <style>
    .center_svg {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: {percentage}%;}}

    .center_txt {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: {percentage}%;}}

    h1{{font-size:50px;}}
    h2{{font-size:40px;}}
    p{{font-size:20px;}}

    table {{
            border-collapse: collapse;
            width: 100%;}}

    td, th {{
            font-size:20px;
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;}}

    tr:nth-child(even) {{
            background-color: #dddddd;}}

    table th {{
        background-color: black;
        color: white;}}

    </style>

    <body>

    <div class="center_txt">

    <h1 align="center">Taptimise Report - Village: {name}</h1>

    <p> This report has been generated using Taptimise the tap positioning 
        Monte-Carlo-Annealing optimiser. For more information and bug reporting 
        visit <a href="https://github.com/ConorWilliams/taptimise">GitHub</a>.
        </p>

    <p> Copyright 2019 C. J. Williams (CHURCHILL COLLEGE). Taptimise is free 
        (open-source) software with ABSOLUTELY NO WARRANTY, licensed under the 
        MIT license</p>

    <p> The arguments & flags given to produce this report where: 
        "{' '.join(sys.argv[1:])}" running Taptimise version {__version__}. </p>

    <p> Taptimise placed <b>{len(taps)} taps</b>, running over <b>{scales} 
        length scales</b>. The furthest tap-house separation was 
        {'{:g}'.format(float('{:.{p}g}'.format(max_dist, p=3)))} units. A 
        summery of the tap percentage loads is: {', '.join(str(tap[3]) for tap in taps)}.
        </p>

    <h2>Village Map</h2>

    </div>

    </div>
    <div class="center_svg">
    {map_svg}
    </div>

    <div class="center_txt">
    <h2>Tap Data</h2>
    {to_html(['Latitude', 'Longitude', 'Number', 'Load %'], taps)}
    <h2>House Data</h2>
    {to_html(['Latitude', 'Longitude', 'Tap Number', 'Walking Dist'], houses)}
    <h2>Debug Visualisations</h2>
    </div>

    </div>
    <div class="center_svg">
    {''.join(debug_svg)}
    </div>

    </body>
    </html>'''

    with open(f"{path[:-4]}_report.html", "w") as html:
        html.write(raw_html)
