import math

import pytest
from pyproj import Transformer

from modules.overlay import shiftBounds
from utils import tiles

TO_MERC = Transformer.from_crs(4326, 3857, always_xy=True)


def slippy_corner(x, y, z):
    '''north-west corner of 256-pixel tile x/y at zoom z'''
    n = 2 ** z
    return x / n * 360 - 180, math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))


@pytest.mark.parametrize('x,y,z', [(30000, 46000, 17), (123, 456, 10), (65536, 65536, 17)])
def test_footprint_of_a_tile_matches_its_slippy_map_bounds(x, y, z):
    west, north = TO_MERC.transform(*slippy_corner(x, y, z))
    east, south = TO_MERC.transform(*slippy_corner(x + 1, y + 1, z))
    lon, lat = tiles.mercator_to_lonlat((west + east) / 2, (south + north) / 2)
    assert tiles.footprint(lon, lat, z, 256, 256) == pytest.approx((west, south, east, north), abs=1e-4)


def test_projection_matches_pyproj():
    for lon, lat in [(0, 0), (-93.5, 45.1), (155.2, -20.7)]:
        assert tiles.lonlat_to_mercator(lon, lat) == pytest.approx(TO_MERC.transform(lon, lat), abs=1e-6)
        assert tiles.mercator_to_lonlat(*tiles.lonlat_to_mercator(lon, lat)) == pytest.approx((lon, lat))


def test_ground_resolution_matches_resolution_table():
    # libs/zoomLevelResolution.csv: zoom 17 -> 1.19 m (0 deg), 0.84 m (45 deg)
    assert tiles.ground_resolution(17, 0) == pytest.approx(1.19, abs=0.005)
    assert tiles.ground_resolution(17, 45) == pytest.approx(0.84, abs=0.005)


def test_shift_as_fraction_and_meters():
    bounds = (0, 0, 100, 50)
    assert shiftBounds(bounds, 0.1, -0.2, 0) == pytest.approx((-10, 10, 90, 60))
    # 10 m on the ground at 60 degrees are 20 Web Mercator units
    assert shiftBounds(bounds, 10, 0, 1, lat=60) == pytest.approx((-20, 0, 80, 50))
