"""
Script to download Open Street Map data of land use. Converts to GeoJSON
Lukas Arnold
WB-DIME
Jan 31 2017

Usage:
	python cv4ag.py parse -s OSM_Query --arg1 Minnesota --arg2 landuse=farmland --key crop

'arg1': Area: place name or ISO country code (looked up with Nominatim), or
	boundary box "west south east north" in degrees
'arg2': OSM tag to search for, e.g. landuse or landuse=farmland
'arg3': Output folder
'arg4': Part of the data to keep (0-1)
"""
import json
import os
import sys
from math import floor

import requests
from shapely.geometry import LineString, Polygon, mapping
from shapely.ops import polygonize, unary_union

from utils.overpass_client import OverpassClient, USER_AGENT

# Query string to OSM to provide land use data with geometries, with the
# query key later placed in the middle
query_template = '''
(
  way[{query}]({{query_bb_s}},{{query_bb_w}},{{query_bb_n}},{{query_bb_e}});
  relation[{query}][type=multipolygon]({{query_bb_s}},{{query_bb_w}},{{query_bb_n}},{{query_bb_e}});
);
out geom;
'''
NOMINATIM_ENDPOINT = 'https://nominatim.openstreetmap.org/search'
MAX_QUERIES_WITHOUT_PROMPT = 100

datatype="GeoJSON"

def getBBox(area):
	'''area name and boundary box (west,south,east,north) of a place or "w s e n" string'''
	try:
		w,s,e,n=[float(v) for v in area.replace(","," ").split()]
		return "bbox_%g_%g_%g_%g" % (w,s,e,n),(w,s,e,n)
	except ValueError:
		pass
	if len(area)==2 and area.isalpha(): # ISO country code
		params={'country':area}
	else:
		params={'q':area}
	params.update({'format':'jsonv2','limit':1})
	response=requests.get(NOMINATIM_ENDPOINT,params=params,
		headers={'User-Agent':USER_AGENT},timeout=60)
	response.raise_for_status()
	results=response.json()
	if not results:
		print("Error: No place found for",area)
		sys.exit(1)
	print("Acquiring data for",results[0]['display_name'])
	s,n,w,e=[float(v) for v in results[0]['boundingbox']]
	return area,(w,s,e,n)

def wayGeometry(geometry):
	return [(p['lon'],p['lat']) for p in geometry]

def elementPolygon(element):
	'''(Multi)Polygon of a closed way or multipolygon relation, None for anything else'''
	if element['type']=='way':
		coords=wayGeometry(element.get('geometry',[]))
		if len(coords)<4 or coords[0]!=coords[-1]: # not an area
			return None
		polygon=Polygon(coords)
	elif element['type']=='relation':
		rings={'outer':[],'inner':[]}
		for member in element.get('members',[]):
			if member['type']=='way' and member.get('role') in rings and member.get('geometry'):
				rings[member['role']].append(LineString(wayGeometry(member['geometry'])))
		outer=unary_union(list(polygonize(rings['outer'])))
		inner=unary_union(list(polygonize(rings['inner'])))
		polygon=outer.difference(inner)
	else:
		return None
	if not polygon.is_valid:
		polygon=polygon.buffer(0)
	if polygon.is_empty or polygon.geom_type not in ('Polygon','MultiPolygon'):
		return None
	return polygon

def toGeoJSON(elements,key):
	'''GeoJSON FeatureCollection; the value of tag key is stored in "Descriptio"'''
	features=[]
	for element in elements:
		tags=element.get('tags',{})
		if key not in tags:
			continue
		polygon=elementPolygon(element)
		if polygon is None:
			continue
		properties=dict(tags)
		properties['Descriptio']=tags[key]
		properties['osm_id']=element['type']+'/'+str(element['id'])
		features.append({'type':'Feature','properties':properties,'geometry':mapping(polygon)})
	return {'type':'FeatureCollection',
		'crs':{'type':'name','properties':{'name':'urn:ogc:def:crs:EPSG::4326'}},
		'features':features}

def script(countryISO='US',query='landuse',outputFolder='data/',partOfData=1,
	outputFile='OSMdata_'):
	"""
	Main function executed by top

	'countryISO': Country, place or boundary box ("w s e n") for which data should be downloaded
	'query': Tag for OSM query to search for
	'partOfData': Part of total data of a country to be processed
	Returns list with [filename,datatype], where datatype is the
		GDAL_CODE
	"""
	partOfData=float(partOfData)
	name,(w,s,e,n)=getBBox(countryISO)
	print("Coordinates:",w,s,e,n)
	print("Key:",query)
	# Area is split into boxes of about 1/8 degree, as (for large countries)
	# the sample is too big (timeout)
	# Number of Boxes = (samples-1)^2 boxes.
	mindiff=min([abs(w-e),abs(n-s)])
	samples=int(floor((mindiff*8)+2))
	print("Number of queries:",(samples-1)**2)
	if (samples-1)**2>MAX_QUERIES_WITHOUT_PROMPT:
		if input("This is a large area. Continue? (y/n) ").lower()!="y":
			sys.exit(0)
	#Get Elements from OSM
	overpass_client = OverpassClient(endpoint='de')
	d = overpass_client.get_bbox_elements(
	    ql_template=query_template.format(query=query),
	    bb_s=s, bb_w=w, bb_n=n, bb_e=e,
	    samples=samples)
	print('Total elements found: %d' % len(d))
	d=d[0:int(floor(partOfData*len(d)))]

	geojson=toGeoJSON(d,query.split('=')[0])
	print("Areas converted to GeoJSON:",len(geojson['features']))
	os.makedirs(outputFolder,exist_ok=True)
	fileName=os.path.join(outputFolder,outputFile+name.replace(" ","_").replace(",","")+".json")
	with open(fileName,'w') as f:
		json.dump(geojson,f)
	print("Written to",fileName)
	return [fileName,datatype]
