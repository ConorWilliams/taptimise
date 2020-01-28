# -*- coding: utf-8 -*-

"""taptimise.taptimise: provides entry point main()."""

import argparse
import csv
import os
import io
import sys
import statistics
from decimal import Decimal

import simplekml
import numpy as np
from pyfiglet import Figlet
from matplotlib import pyplot as plt


from .__init__ import __version__
from .optimise import optimise
from .htmltable import to_html
from .units import LocalXY

WINDOW_SIZE = 3  # must be an odd number


def smooth(a, WSZ=WINDOW_SIZE):
    # a: NumPy 1-D array containing the data to be smoothed
    # WSZ: smoothing window size needs, which must be odd number,
    # as in the original MATLAB implementation
    if len(a) < WSZ:
        return a
    out0 = np.convolve(a, np.ones(WSZ, dtype=int), "valid") / WSZ
    r = np.arange(1, WSZ - 1, 2)
    start = np.cumsum(a[: WSZ - 1])[::2] / r
    stop = (np.cumsum(a[:-WSZ:-1])[::2] / r)[::-1]
    return np.concatenate((start, out0, stop))


def save_svg(fig):
    # saves a matplotlib figure object to an html embeddable svg string
    w, h = fig.get_size_inches()
    w, h = round(w + 0.5), round(h + 0.5)

    fig.set_size_inches(w, h)

    w, h = int(72 * w), int(72 * h)

    tmp = io.StringIO()
    fig.savefig(tmp, format="svg")

    svg = "<svg" + tmp.getvalue().split("<svg")[1]

    svg = svg.replace(f'height="{h}pt"', 'height="100vmin"', 1)
    svg = svg.replace(f'width="{w}pt"', 'width="auto"', 1)

    return svg


def formatter(prog):
    return argparse.HelpFormatter(prog, max_help_position=52)


def main():
    custom_fig = Figlet(font="graffiti")
    print(custom_fig.renderText("Taptimise"))
    print("Tap placement optimiser with Monte-Carlo-Annealer")
    print("Copyright 2019 C. J. Williams (CHURCHILL COLLEGE)")
    print("This is free software with ABSOLUTELY NO WARRANTY")
    print()

    # ****************************************************************************
    # *                              Parse Arguments                             *
    # ****************************************************************************

    parser = argparse.ArgumentParser(formatter_class=formatter)
    group = parser.add_mutually_exclusive_group(required=True)

    parser.add_argument("path", help="Path to house data.")  # positional

    parser.add_argument(
        "-V", "--version", action="version", version="%(prog)s " + __version__
    )
    group.add_argument(
        "-t",
        "--tap-capacity",
        type=float,
        action="store",
        metavar="CAP",
        help="Maximum load a single tap can support.",
    )
    group.add_argument(
        "-N",
        "--num-taps",
        type=int,
        action="store",
        help="Set the number of taps to start with.",
        metavar="NUM",
    )
    parser.add_argument(
        "-m",
        "--max-distance",
        type=float,
        default=-1,
        help="Maximum house-tap distance.",
        action="store",
        metavar="DIST",
    )
    parser.add_argument(
        "-b",
        "--buffer-size",
        type=int,
        action="store",
        help="Size of each houses internal buffer.",
        metavar="SIZE",
    )
    parser.add_argument(
        "-f",
        "--fairness",
        type=int,
        action="store",
        default=50,
        help="Higher equals flatter load distibution but longer walking distances. On interval 1-1000000.",
        metavar="FAIR",
    )
    parser.add_argument(
        "-s",
        "--steps",
        action="store",
        type=int,
        help="Number of Monte-Carlo cooling steps per scale per tap.",
    )
    parser.add_argument(
        "--scribble",
        action="store",
        metavar="DEMAND",
        type=float,
        help="Set parser for scribble maps file argument is per house demand.",
    )
    parser.add_argument(
        "--scales",
        action="store",
        type=int,
        help="Set number of scales, leave blank for automatic detection.",
    )
    parser.add_argument(
        "--csv", action="store_true", help="Write results to a .csv file."
    )
    parser.add_argument(
        "--kml", action="store_true", help="Write results to a .kml file."
    )
    parser.add_argument(
        "--no-relax",
        action="store_true",
        help="Disables extra relaxation optimisation.",
    )
    parser.add_argument(
        "--no-auto",
        action="store_true",
        help="Disables automatic reruns when max house-tap separation too large.",
    )
    parser.add_argument(
        "--no-debug", action="store_false", help="Disable debugging graphs."
    )

    args = parser.parse_args()

    if os.path.isabs(args.path):
        path = os.path.normpath(args.path)
    else:
        path = os.path.abspath(args.path)

    # ****************************************************************************
    # *                             Run Optimisation                             *
    # ****************************************************************************

    raw_houses = []

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        if args.scribble is not None:
            for row in reader:
                try:
                    if row[0] == "Marker":
                        raw_houses.append(
                            [float(row[4]), float(row[5]), float(args.scribble)]
                        )
                except:
                    print("Can't read", row)
        else:
            for row in reader:
                try:
                    raw_houses.append([float(elem) for elem in row])
                except:
                    print("Can't read", row)

    convert = LocalXY(*raw_houses[0][0:2])

    for h in raw_houses:
        h[0], h[1] = convert.geo2enu(h[0], h[1])

    if args.tap_capacity is None:
        args.tap_capacity = sum(h[2] for h in raw_houses) / args.num_taps

    max_dist = args.max_distance + 1
    num_taps = args.num_taps

    while max_dist > args.max_distance:
        houses, taps, max_dist, run_data, energy = optimise(
            raw_houses,
            args.tap_capacity,
            num_taps=num_taps,
            steps=args.steps,
            debug=args.no_debug,
            multiscale=args.scales,
            max_dist=args.max_distance,
            buff_size=args.buffer_size,
            norelax=args.no_relax,
            fair=args.fairness,
        )
        num_taps = len(taps) + 1

        print()

        if args.no_auto or args.max_distance < 0:
            break

    # ****************************************************************************
    # *                               Plot Village                               *
    # ****************************************************************************

    name = os.path.basename(args.path)[:-4]

    cmap = plt.cm.get_cmap("nipy_spectral", len(taps))

    h = np.asarray(houses)
    t = np.asarray(taps)

    fig, ax = plt.subplots(figsize=(6, 6))

    ax.scatter(h[::, 0], h[::, 1], c=h[::, 2], cmap=cmap, label="Houses", s=4)
    ax.plot(t[:, 0], t[:, 1], "+", color="k", markersize=8, label="Taps")

    ax.set_title(f"{name.upper()} - {len(taps)} Taps")
    ax.set_aspect("equal")

    ax.set_ylabel("Latitude")
    ax.set_xlabel("Longitude")

    xmin, xmax = h[::, 0].min(), h[::, 0].max()
    ymin, ymax = h[::, 1].min(), h[::, 1].max()

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

    if args.no_debug:

        width = 1

        E0 = run_data[0][0][1]

        for order, run in enumerate(run_data):

            fig, ax = plt.subplots()

            data = np.asarray(run)
            ind = np.arange(len(run))

            counts = data[::, 2:5:1] * 100 / len(houses)

            counts[::, 1] += counts[::, 0]
            counts[::, 2] += counts[::, 1]

            counts[::, 0] = smooth(counts[::, 0])
            counts[::, 1] = smooth(counts[::, 1])

            ax.set_xlabel("Monte-Carlo Steps")
            ax.set_ylabel("Percentage Count")
            ax.set_title(f"Cooling Curve")

            ax.fill_between(
                ind, counts[::, 0], label="Favourable", color="mediumseagreen"
            )
            ax.fill_between(
                ind,
                counts[::, 0],
                counts[::, 1],
                label="Unfavourable-accepted",
                color="indianred",
            )
            ax.fill_between(
                ind,
                counts[::, 1],
                counts[::, 2],
                label="Unfavourable-rejected",
                color="steelblue",
            )
            ax.fill_between(
                ind, counts[::, 2], 100, label="Quantum-tunnel", color="orchid"
            )

            ax.set_xlim(ind[0], ind[-1])
            ax.set_ylim(bottom=0)
            ax.legend(loc="center right")

            ax2 = ax.twinx()

            ax2.set_ylabel("Relative Energy")
            ax2.plot(ind, smooth(data[::, 1]), color="k")

            fig.tight_layout()

            svg = save_svg(fig)

            debug_svg.append(svg)

        print("Total final energy is: ", f"{Decimal(energy):.2E}")

    print("The biggest walk is:", max_dist)
    print("Percentage loads:", ", ".join(str(tap[3]) for tap in taps))

    # ****************************************************************************
    # *                                 Make html                                *
    # ****************************************************************************

    for t in taps:
        t[0], t[1], t[3] = *convert.enu2geo(t[0], t[1]), int(t[3])
        t[0], t[1] = float(t[0]), float(t[1])

    for h in houses:
        h[0], h[1], h[3] = *convert.enu2geo(h[0], h[1]), int(h[3])
        h[0], h[1] = float(h[0]), float(h[1])

    houses.sort(key=lambda x: x[2])

    if args.csv:
        with open(f"{path[:-4]}_taps.csv", "w") as f:
            for t in taps:
                print(f"{round(t[0], 5)},{round(t[1], 5)}", file=f)

    if args.kml:
        kml = simplekml.Kml()
        for t in taps:
            # long, lat for simplekml!
            kml.newpoint(name="Tap", coords=[(t[1], t[0])])

        for h in houses:
            kml.newpoint(name="House", coords=[(h[1], h[0])])

        kml.save(f"{path[:-4]}_taps.kml")

    percentage = 50
    raw_html = f"""
    <!DOCTYPE html>
    <html>

    <head>
    <title> Taptimise {name.upper()} Report </title>
    </head>

    <style>
    .center_svg {{
        display: block;
        margin-left: auto;
        margin-right: auto;}}

    .center_txt {{
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 80vmin;}}

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

    <h1 align="center">Taptimise Report - Village: {name.upper()}</h1>

    <p> This report has been generated using Taptimise the tap positioning
        Monte-Carlo-Annealing optimiser. For more information and bug reporting
        visit <a href="https://github.com/ConorWilliams/taptimise">GitHub</a>.
        </p>

    <p> Copyright 2019 C. J. Williams (CHURCHILL COLLEGE). Taptimise is free
        (open-source) software with ABSOLUTELY NO WARRANTY, distibuted under the
        MIT license.
        </p>

    <p> The arguments & flags given to produce this report where:
        "{' '.join(sys.argv[1:])}" running Taptimise version {__version__}.
        </p>

    <p> Taptimise placed <b>{len(taps)} taps</b>. The furthest tap-house separation was
        <b>{'{:g}'.format(float('{:.{p}g}'.format(max_dist, p=3)))} meters</b>.
        The final energy of the village was <b>{Decimal(energy):.2E}
        units </b>. A summery of the tap loads are:
        {', '.join(str(tap[3]) for tap in taps)}. With a mean of
        <b>{round(statistics.mean(t[3] for t in taps))} ±
        {round(statistics.pstdev(t[3] for t in taps))}</b>.
        </p>

    <h2>Village Map</h2>

    </div>


    <div class="center_svg">
    {map_svg}
    </div>

    <div class="center_txt">
    <h2>Annealing Data</h2>
    </div>

    <div class="center_svg">
    {''.join(debug_svg)}
    </div>

    <div class="center_txt">
    <h2>Tap Data</h2>
    {to_html(['Latitude', 'Longitude', 'Number', 'Load'], taps)}
    <h2>House Data</h2>
    {to_html(['Latitude', 'Longitude', 'Tap Number', 'Separation/m'], houses)}
    </div>


    </body>
    </html>"""

    with open(f"{path[:-4]}_report.html", "w") as html:
        html.write(raw_html)
