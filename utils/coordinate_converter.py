'''Lukas Arnold
transform coordinates'''

import pyproj as pyproj # Import the pyproj module

class CoordConvert(object):
	def __init__(self):
		# Common projections using EPSG codes
		self.wgs84=pyproj.Proj("+init=EPSG:4326") # LatLon with WGS84 datum used by GPS units and Google Earth
		#self.osgb36=pyproj.Proj("+init=EPSG:27700") # UK Ordnance Survey, 1936 datum
	
	def getCoordSystem(self,geojson):
		name= geojson['crs']['properties']['name']
		if "EPSG".lower() in name.lower():
			print "Identified coordinate system is EPSG:"+str(name[-4:])
			code=str(name[-4:])
		else:
			code=str(4326)  #if not found, assume standard format
		self.epsg=pyproj.Proj("+init=EPSG:"+code))
		return int(code)
	
	def convert(self,lat,lon):
		'''converts to wgs84'''
		return pyproj.transform(self.epsg, self.wgs84, lat, lon)
			
