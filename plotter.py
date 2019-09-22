
import sys
import csv

import numpy as np
from matplotlib import pyplot as plt

from taptimise.units import LocalXY

taps = []

with open(sys.argv[1], newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    for row in reader:
        taps.append([row[0], row[1]])

houses = []

taps.sort(key=lambda x: x[0])

for t in taps:
    print(t)

with open(sys.argv[2], newline='', encoding='utf-8-sig') as f:
    reader = csv.reader(f)

    for row in reader:
        try:
            if row[0] == 'Marker':
                houses.append(
                    [float(row[4]), float(row[5])])
        except:
            print('Can\'t read', row)


name = sys.argv[1]

h = np.asarray(houses)
t = np.asarray(taps)

fig, ax = plt.subplots(figsize=(6, 6))

ax.plot(h[::, 0], h[::, 1], '.', c='b', label='Houses')
ax.plot(t[:, 0], t[:, 1], '+', color='k', markersize=8, label='Taps')

ax.set_title(f"{name.upper()} - {len(taps)} Taps")
ax.set_aspect('equal')

ax.set_ylabel('Latitude')
ax.set_xlabel('Longitude')

xmin, xmax = h[::, 0].min(), h[::, 0].max()
ymin, ymax = h[::, 1].min(), h[::, 1].max()

gap = max(xmax - xmin, ymax - ymin)

# ax.set_xlim((xmin, xmin + gap))
# ax.set_ylim((ymin, ymin + gap))

# ax.xaxis.set_ticklabels([])
# ax.yaxis.set_ticklabels([])

# ax.set_xticks([])
# ax.set_yticks([])

ax.legend()

fig.tight_layout()

plt.show()
