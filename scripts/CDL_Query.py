"""
Script to get crop types from the USDA Cropland Data Layer (CDL, 30 m, public
domain, contiguous US, 2008-2021 on Planetary Computer). Converts to GeoJSON.

Usage:
	python cv4ag.py parse -s CDL_Query --arg1 "Le Sueur County, Minnesota" --arg2 2021 --arg4 Corn,Soybeans

'arg1': Area: place name (looked up with Nominatim) or boundary box
	"west south east north" in degrees
'arg2': Year (use the same year for the NAIP imagery, crops rotate)
'arg3': Output folder
'arg4': Classes to keep, comma separated (default: all). Other land is background.
"""
import os
import sys

import geopandas as gpd
import numpy as np
import rasterio
import requests
from rasterio.features import shapes, sieve
from rasterio.merge import merge
from rasterio.warp import transform_bounds
from shapely.geometry import shape

from utils import planetary_computer
from utils.places import getBBox

COLLECTION = 'usda-cdl'
CRS = 'EPSG:5070'  # CONUS Albers, the projection of the CDL
# connected areas smaller than this (in 30 m pixels) are merged into their
# neighbours: single misclassified pixels are noise at field scale
MIN_PIXELS = 5

datatype = "GeoJSON"


def classNames():
	'''CDL value -> class name'''
	collection = requests.get(planetary_computer.STAC_API + '/collections/' + COLLECTION,
		timeout=60).json()
	return {c['value']: c['description'] for c in
		collection['item_assets']['cropland']['classification:classes']}


def readCDL(bbox, year):
	'''CDL class values and transform (EPSG:5070) for bbox (degrees)'''
	items = [item for item in planetary_computer.search(COLLECTION, bbox,
		planetary_computer.year_range(year)) if item['id'].startswith('cropland_%s_' % year)]
	if not items:
		print("Error: No CDL data of", year, "for this area (contiguous US, 2008-2021).")
		sys.exit(1)
	print("CDL tiles:", len(items))
	with rasterio.Env(**planetary_computer.GDAL_ENV):
		sources = [rasterio.open(planetary_computer.sign(item['assets']['cropland']['href'],
			COLLECTION)) for item in items]
		try:
			data, transform = merge(sources, bounds=transform_bounds('EPSG:4326', CRS, *bbox),
				nodata=0)
		finally:
			for src in sources:
				src.close()
	return data[0], transform


def toGeoJSON(data, transform, names, classes=None, minpixels=MIN_PIXELS):
	'''
	polygons of the CDL classes (all, or the class names in classes), with the
	class name in "Descriptio" and the CDL value in "cdl_code"
	'''
	data = sieve(data, size=minpixels) if minpixels > 1 else data
	keep = data > 0
	if classes:
		values = [v for v, name in names.items() if name in classes]
		missing = set(classes) - {names[v] for v in values}
		if missing:
			print("Error: Unknown CDL classes:", ", ".join(sorted(missing)))
			sys.exit(1)
		keep &= np.isin(data, values)
	polygons = [(shape(geometry), int(value)) for geometry, value in
		shapes(data, mask=keep, transform=transform)]
	return gpd.GeoDataFrame({
		'Descriptio': [names.get(v, str(v)) for _, v in polygons],
		'cdl_code': [v for _, v in polygons]},
		geometry=[p for p, _ in polygons], crs=CRS)


def script(area='Le Sueur County, Minnesota', year='2021', outputFolder='data/',
	classes=None, outputFile='CDL_'):
	"""
	Main function executed by top

	Returns list with [filename,datatype], where datatype is the
		GDAL_CODE
	"""
	name, bbox = getBBox(area)
	print("Coordinates:", *bbox)
	data, transform = readCDL(bbox, year)
	print("Pixels: %d x %d (30 m)" % (data.shape[1], data.shape[0]))
	classes = [c.strip() for c in classes.split(",")] if classes else None
	features = toGeoJSON(data, transform, classNames(), classes)
	print("Areas converted to GeoJSON:", len(features))
	os.makedirs(outputFolder, exist_ok=True)
	fileName = os.path.join(outputFolder, outputFile + name.replace(" ", "_").replace(",", "")
		+ "_" + str(year) + ".json")
	if os.path.exists(fileName):
		os.remove(fileName)
	features.to_file(fileName, driver="GeoJSON")
	print("Written to", fileName)
	return [fileName, datatype]
