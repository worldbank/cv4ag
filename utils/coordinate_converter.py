'''Lukas Arnold
transform coordinates'''

from pyproj import Transformer
from modules.getFeatures import find_between

class CoordConvert(object):
	def getCoordSystem(self,geojson,epsg=None):
		''' initialise coordinate system according to geojson file '''
		if epsg:
			code=epsg
		else:
			try:
				name= geojson['crs']['properties']['name']
				if "epsg" in name.lower():
					code=find_between(name, ':')
					print("Identified coordinate system is EPSG:"+str(code))
				else:
					code=4326  #if not found, assume standard format
					print("Assuming format EPSG:"+str(code),"for",name)
			except KeyError:
				code=4326  #GeoJSON without crs member is WGS84 (RFC 7946)
				print("No coordinate system in GIS file. Assuming EPSG:4326 (use --epsg to override).")
		if int(code)!=9999:
			self.toWgs84=Transformer.from_crs(int(code),4326,always_xy=True)
			self.fromWgs84=Transformer.from_crs(4326,int(code),always_xy=True)
		return int(code)

	def convert(self,lon,lat):
		'''
		converts to wgs84
		return (longitude,latitude) (!)
		'''
		return self.toWgs84.transform(lon,lat)

	def convertBack(self,lon,lat):
		'''
		converts from wgs84
		return (longitude,latitude) (!)
		'''
		return self.fromWgs84.transform(lon,lat)
