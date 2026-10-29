'''
Web Mercator (EPSG:3857) footprint of static satellite images.

Static map images are Web Mercator renders, so the area an image covers is an
exact rectangle in EPSG:3857 and the class labels are rasterized in that
projection. Zoom levels follow the 256-pixel tile convention used throughout
cv4ag (zoom 17 ~ 1.19 m/pixel at the equator, see libs/zoomLevelResolution.csv).
'''
import math

EARTH_RADIUS = 6378137.0
MERCATOR_CRS = "EPSG:3857"

def lonlat_to_mercator(lon,lat):
	x = EARTH_RADIUS*math.radians(lon)
	y = EARTH_RADIUS*math.log(math.tan(math.pi/4+math.radians(lat)/2))
	return x,y

def mercator_to_lonlat(x,y):
	lon = math.degrees(x/EARTH_RADIUS)
	lat = math.degrees(2*math.atan(math.exp(y/EARTH_RADIUS))-math.pi/2)
	return lon,lat

def resolution(zoom):
	'''size of one pixel in EPSG:3857 units'''
	return 2*math.pi*EARTH_RADIUS/(256*2**zoom)

def ground_resolution(zoom,lat):
	'''size of one pixel in meters on the ground at latitude lat'''
	return resolution(zoom)*math.cos(math.radians(lat))

def footprint(lon,lat,zoom,width,height):
	'''
	bounds (west,south,east,north) in EPSG:3857 of a width x height image
	centered on lon/lat at zoom level zoom
	'''
	x,y = lonlat_to_mercator(lon,lat)
	r = resolution(zoom)
	return (x-width/2*r, y-height/2*r, x+width/2*r, y+height/2*r)
