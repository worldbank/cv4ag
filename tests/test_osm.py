from shapely.geometry import shape

from scripts.OSM_Query import toGeoJSON
from utils.places import getBBox


def geometry(coords):
    return [{'lon': x, 'lat': y} for x, y in coords]


SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
HOLE = [(0.4, 0.4), (0.6, 0.4), (0.6, 0.6), (0.4, 0.6), (0.4, 0.4)]

ELEMENTS = [
    {'type': 'way', 'id': 1, 'tags': {'landuse': 'farmland', 'crop': 'corn'}, 'geometry': geometry(SQUARE)},
    # open way: not an area
    {'type': 'way', 'id': 2, 'tags': {'landuse': 'farmland'}, 'geometry': geometry(SQUARE[:-1])},
    # tag missing
    {'type': 'way', 'id': 3, 'tags': {'highway': 'track'}, 'geometry': geometry(SQUARE)},
    # outer ring split over two ways, with a hole
    {'type': 'relation', 'id': 4, 'tags': {'landuse': 'meadow', 'type': 'multipolygon'}, 'members': [
        {'type': 'way', 'ref': 10, 'role': 'outer', 'geometry': geometry(SQUARE[:3])},
        {'type': 'way', 'ref': 11, 'role': 'outer', 'geometry': geometry(SQUARE[2:])},
        {'type': 'way', 'ref': 12, 'role': 'inner', 'geometry': geometry(HOLE)}]},
]


def test_osm_elements_to_geojson():
    geojson = toGeoJSON(ELEMENTS, 'landuse')
    features = {f['properties']['osm_id']: f for f in geojson['features']}
    assert sorted(features) == ['relation/4', 'way/1']
    assert features['way/1']['properties']['Descriptio'] == 'farmland'
    assert features['way/1']['properties']['crop'] == 'corn'
    assert shape(features['way/1']['geometry']).area == 1
    assert shape(features['relation/4']['geometry']).area == 1 - 0.04
    assert features['relation/4']['properties']['Descriptio'] == 'meadow'


def test_bbox_string_needs_no_lookup():
    assert getBBox('-93.5 45 -93.4 45.1') == ('bbox_-93.5_45_-93.4_45.1', (-93.5, 45, -93.4, 45.1))
