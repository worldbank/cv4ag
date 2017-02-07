'''Lukas Arnold
transform coordinates'''

import pyproj as pyproj # Import the pyproj module
from modules.getFeatures import find_between

class CoordConvert(object):
	def __init__(self):
		# Common projections using EPSG codes
		self.wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
		#self.osgb36=pyproj.Proj("+init=EPSG:27700") # UK Ordnance Survey, 1936 datum
	
	def getCoordSystem(self,geojson):
		''' initialise coordinate system according to geojson file '''
		try:
			name= geojson['crs']['properties']['name']
			if "EPSG".lower() in name.lower():
				code=find_between(name, ':')
				print "Identified coordinate system is EPSG:"+str(code)
			else:
				code=str(4326)  #if not found, assume standard format
		except KeyError:
			code=raw_input("EPSG Code for projection not found. Enter EPSC code manually: ")
		self.epsg=pyproj.Proj("+init=EPSG:"+code)
		return int(code)
	
	def convert(self,lon,lat):
		'''
		converts to wgs84
		return (longitude,latitude) (!)
		'''
		return pyproj.transform(self.epsg, self.wgs84, lon, lat)
			
	def convertBack(self,lon,lat):
		'''
		converts from wgs84
		return (longitude,latitude) (!)
		'''
		return pyproj.transform(self.wgs84, self.epsg, lon, lat)
