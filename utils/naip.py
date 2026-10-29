'''
Satellite tiles from NAIP aerial imagery (USDA National Agriculture Imagery
Program, public domain, contiguous US, ~0.6-1 m). Images are reprojected onto
the same Web Mercator tile grid as static map images.
'''
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_bounds
from rasterio.vrt import WarpedVRT
from shapely.geometry import box, shape

from utils import planetary_computer, tiles

COLLECTION = 'naip'


class NaipTiles(object):
    def __init__(self, bbox, year, items=None, signed=True):
        '''
        NAIP images of year within bbox (west,south,east,north in degrees).
        items: list of (footprint in degrees, href, date), searched if not given
        '''
        if items is None:
            items = [(shape(item['geometry']), item['assets']['image']['href'],
                      item['properties']['datetime'])
                     for item in planetary_computer.search(
                         COLLECTION, bbox, planetary_computer.year_range(year))]
        # latest images first
        self._items = sorted(items, key=lambda item: item[2], reverse=True)
        self._signed = signed
        print('NAIP images of %s found: %d' % (year, len(self._items)))

    def __len__(self):
        return len(self._items)

    def read(self, bounds, width, height):
        '''
        RGB image (height x width x 3, uint8) covering bounds (EPSG:3857) and
        the fraction of pixels with data
        '''
        west, south = tiles.mercator_to_lonlat(bounds[0], bounds[1])
        east, north = tiles.mercator_to_lonlat(bounds[2], bounds[3])
        footprint = box(west, south, east, north)
        image = np.zeros((3, height, width), dtype=np.uint8)
        valid = np.zeros((height, width), dtype=bool)
        transform = from_bounds(*bounds, width, height)
        with rasterio.Env(**planetary_computer.GDAL_ENV):
            for geometry, href, _ in self._items:
                if not geometry.intersects(footprint):
                    continue
                if self._signed:
                    href = planetary_computer.sign(href, COLLECTION)
                # NAIP has no nodata value: the alpha band marks pixels
                # outside of the image
                with rasterio.open(href) as src, WarpedVRT(
                        src, crs=tiles.MERCATOR_CRS, transform=transform,
                        width=width, height=height, add_alpha=True,
                        resampling=Resampling.bilinear) as vrt:
                    data = vrt.read(indexes=[1, 2, 3])
                    fill = (vrt.read(vrt.count) == 255) & ~valid
                image[:, fill] = data[:, fill]
                valid |= fill
                if valid.all():
                    break
        return image.transpose(1, 2, 0), valid.mean()
