import pymap3d as p3d

# Shallow wrapper to pymap3d's local tangent plane coordinate transforms


class LocalXY():
    def __init__(lat0, lon0):
        self.lat0 = lat0
        self.lon0 = lon0

    def geo2enu(lat, lon):
        x, y, _ = p3d.geodetic2enu(
            lat, lon, 0, self.lat0, self.lon0, 0, deg=True)

        return x, y

    def enu2geo(x, y):
        lat, lon = enu2geodetic(x, y, 0, sel.lat0, self.lon0, 0, deg=True)
