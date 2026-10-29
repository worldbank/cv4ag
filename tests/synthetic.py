'''
Synthetic agricultural data: rectangular fields in UTM coordinates and
satellite tiles rendered from them independently of cv4ag's overlay code
(pixel centers are reprojected one by one with pyproj).
'''
import json
import math
import os

import numpy as np
import shapely
from PIL import Image
from pyproj import Transformer
from shapely.geometry import box, mapping

UTM = 32615  # Minnesota
CLASSES = ['corn', 'soy', 'wheat']
COLORS = {0: (140, 110, 80), 1: (60, 140, 50), 2: (200, 190, 80), 3: (30, 80, 40)}


def make_fields(origin=(450000, 5000000), n=12, size=120, gap=20, seed=0):
    '''n x n grid of fields with crop type in property "crop" (some left empty)'''
    rng = np.random.default_rng(seed)
    features = []
    for i in range(n):
        for j in range(n):
            r = rng.random()
            if r < 0.15:
                continue  # background
            crop = CLASSES[0] if r < 0.6 else CLASSES[1] if r < 0.85 else CLASSES[2]
            x = origin[0] + i * (size + gap)
            y = origin[1] + j * (size + gap)
            features.append({'type': 'Feature', 'properties': {'crop': crop},
                             'geometry': mapping(box(x, y, x + size, y + size))})
    return {'type': 'FeatureCollection',
            'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:EPSG::%d' % UTM}},
            'features': features}


def render_tile(fields, lon, lat, zoom, width, height, seed=0):
    '''image and true label of a Web Mercator tile centered on lon/lat'''
    res = 2 * math.pi * 6378137 / (256 * 2 ** zoom)
    to_merc = Transformer.from_crs(4326, 3857, always_xy=True)
    to_utm = Transformer.from_crs(3857, UTM, always_xy=True)
    cx, cy = to_merc.transform(lon, lat)
    col, row = np.meshgrid(np.arange(width) + 0.5, np.arange(height) + 0.5)
    mx = cx + (col - width / 2) * res
    my = cy - (row - height / 2) * res
    ux, uy = to_utm.transform(mx.ravel(), my.ravel())
    label = np.zeros(width * height, dtype=np.uint8)
    # less frequent classes on top, like overlay
    order = sorted(fields['features'], key=lambda f: CLASSES.index(f['properties']['crop']))
    for feature in order:
        polygon = shapely.geometry.shape(feature['geometry'])
        inside = shapely.contains_xy(polygon, ux, uy)
        label[inside] = CLASSES.index(feature['properties']['crop']) + 1
    label = label.reshape(height, width)
    rng = np.random.default_rng(seed)
    palette = np.array([COLORS[c] for c in range(4)], dtype=np.float32)
    image = palette[label] + rng.normal(0, 12, (height, width, 3))
    return np.clip(image, 0, 255).astype(np.uint8), label


def make_dataset(folder, ntiles=40, zoom=16, width=160, height=128, seed=0):
    '''writes folder/fields.json and tiles as get_satellite would; returns true labels'''
    fields = make_fields(seed=seed)
    inputFile = os.path.join(folder, 'fields.json')
    with open(inputFile, 'w') as f:
        json.dump(fields, f)
    sat = os.path.join(folder, 'out', 'fields', 'sat')
    os.makedirs(sat)
    to_wgs = Transformer.from_crs(UTM, 4326, always_xy=True)
    rng = np.random.default_rng(seed)
    truth = {}
    with open(os.path.join(sat, 'tiles.csv'), 'w') as f:
        f.write('name,lon,lat,zoom,width,height\n')
        for i in range(ntiles):
            x, y = 450000 + rng.uniform(100, 1500), 5000000 + rng.uniform(100, 1500)
            lon, lat = to_wgs.transform(x, y)
            image, label = render_tile(fields, lon, lat, zoom, width, height, seed=i)
            name = 'fields_%d.png' % i
            Image.fromarray(image).save(os.path.join(sat, name))
            f.write('%s,%.8f,%.8f,%d,%d,%d\n' % (name, lon, lat, zoom, width, height))
            truth[name] = label
    return inputFile, os.path.join(folder, 'out'), truth
