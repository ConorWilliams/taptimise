import pymap3d as p3d


class LocalXY():
    # Shallow wrapper to pymap3d's local tangent plane coordinate transforms.
    # This is required to correct for the curvature of the Earth distorting 
    # lat, long away from the equator.

    def __init__(self, lat0, lon0):
        self.lat0 = lat0
        self.lon0 = lon0

    def geo2enu(self, lat, lon):
        x, y, _ = p3d.geodetic2enu(
            lat, lon, 0, self.lat0, self.lon0, 0, deg=True, ell=p3d.Ellipsoid('wgs84'))

        return x, y

    def enu2geo(self, x, y):
        lat, lon, _ = p3d.enu2geodetic(
            x, y, 0, self.lat0, self.lon0, 0, deg=True, ell=p3d.Ellipsoid('wgs84'))

        return lat, lon
