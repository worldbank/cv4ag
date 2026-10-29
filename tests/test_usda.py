import numpy as np
import rasterio
from pyproj import Transformer
from rasterio.enums import ColorInterp
from rasterio.transform import from_origin
from shapely.geometry import box

from scripts.CDL_Query import toGeoJSON
from utils import tiles
from utils.naip import NaipTiles

UTM = 'EPSG:26915'
TO_WGS = Transformer.from_crs(UTM, 4326, always_xy=True)


def write_naip(path, x0, y0, color, size=500, res=0.6):
    '''4-band image in UTM with a constant RGB color'''
    data = np.zeros((4, size, size), dtype=np.uint8)
    for band, value in enumerate(color):
        data[band] = value
    with rasterio.open(path, 'w', driver='GTiff', width=size, height=size, count=4, dtype='uint8',
                       crs=UTM, transform=from_origin(x0, y0, res, res), photometric='MINISBLACK') as dst:
        dst.write(data)
        dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.undefined]
    corners = [TO_WGS.transform(x, y) for x in (x0, x0 + size * res) for y in (y0, y0 - size * res)]
    return box(min(c[0] for c in corners), min(c[1] for c in corners),
               max(c[0] for c in corners), max(c[1] for c in corners))


def test_naip_tiles_are_mosaicked_from_neighbouring_images(tmp_path):
    x0, y0 = 420000, 4920000
    west = write_naip(str(tmp_path / 'w.tif'), x0, y0, (200, 0, 0))
    east = write_naip(str(tmp_path / 'e.tif'), x0 + 300, y0, (0, 0, 200))
    naip = NaipTiles(None, 2021, signed=False, items=[
        (west, str(tmp_path / 'w.tif'), '2021-06-01'), (east, str(tmp_path / 'e.tif'), '2021-06-01')])
    lon, lat = TO_WGS.transform(x0 + 300, y0 - 150)  # on the edge of the western image
    image, coverage = naip.read(tiles.footprint(lon, lat, 18, 160, 128), 160, 128)
    assert coverage == 1
    assert (image[:, :70] == (200, 0, 0)).all()
    assert (image[:, 90:] == (0, 0, 200)).all()

    lon, lat = TO_WGS.transform(x0, y0 - 150)  # western edge of the data
    image, coverage = naip.read(tiles.footprint(lon, lat, 18, 160, 128), 160, 128)
    assert 0.4 < coverage < 0.6


def test_cdl_polygons_without_speckle_and_with_class_filter():
    data = np.zeros((20, 20), dtype=np.uint8)
    data[:, :10] = 1   # corn
    data[:, 10:] = 5   # soybeans
    data[3, 3] = 5     # single misclassified pixel
    data[15:, 15:] = 141  # forest
    names = {1: 'Corn', 5: 'Soybeans', 141: 'Deciduous Forest'}
    transform = from_origin(0, 600, 30, 30)

    features = toGeoJSON(data, transform, names)
    areas = features.dissolve('Descriptio').area
    assert areas['Corn'] == 200 * 900  # speckle merged into the corn field
    assert areas['Soybeans'] == 175 * 900
    assert set(features.cdl_code) == {1, 5, 141}

    features = toGeoJSON(data, transform, names, classes=['Corn', 'Soybeans'])
    assert set(features.Descriptio) == {'Corn', 'Soybeans'}
