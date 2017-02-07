
'''Lukas Arnold
get coordinates of image by gps-coordinates,library and pixel'''

import pyproj as pyproj # Import the pyproj module
import numpy,csv

class imageCoordinates(object):
	def __init__(self,pixel,library,zoomLevel):
		self.pixel=pixel
		#load csv data. Rows are zoom levels, column are latitude
		#and values are meters per pixel
		with open(library,'rb') as csvfile:
			metersperpixel = list(csv.reader(csvfile,delimiter=","))
		latitudes=[]
		#convert to floats
		for element in metersperpixel[0][1:]:
			latitudes.append(float(element))
		for row in range(1,len(metersperpixel)):
			res_values=[]
			if int(metersperpixel[row][0])==zoomLevel:
			#convert to floats
				for element in metersperpixel[row][1:]:
					res_values.append(float(element))
				self.fitvalues=\
					numpy.polyfit(latitudes, #fit to latitutde values
					res_values, 3)	#3rd degree polynomial fit
				print "Fit done."	
				break

	def toMeter(self,value):
		'''get resolution at latitude 'value'''
		return self.fitvalues[0]*value**3+self.fitvalues[1]*value**2\
			+self.fitvalues[2]*value+self.fitvalues[3]

	def add_meters_lat(self,lat,delta):
		'''Add 'delta' meters to a GPS latitude 'lat'. 
		Positive: To north, negative: to south'''
		return lat+(180/numpy.pi)*(delta/6378137)

	def add_meters_lon(self,lon,lat,delta):
		'''Add 'delta' meters to a GPS longitude 'lon'.
		Positive: To east, negative: to west'''
		#West coordinates are indicated with negative values
		return lon+(180/numpy.pi)*(delta/6378137)/numpy.cos(lat*numpy.pi/180)
	
	def getImageCoord(self,lat,lon):
		''' Get 4 corners of image in wsg84 format.
		Returns [0] latitutes and [1] longitudes '''
		#Get resolution for GPS coordinate
		meterPerPixel=self.toMeter(abs(lat))
		#add pixel/2 to each of the four sides
		lat_upper=self.add_meters_lat(lat,(self.pixel/2)*meterPerPixel)
		
		lon_upperleft=self.add_meters_lon(lon,lat_upper,-(self.pixel/2)*meterPerPixel)
		lon_upperright=self.add_meters_lon(lon,lat_upper,(self.pixel/2)*meterPerPixel)
		
		lat_bottom=self.add_meters_lat(lat,-(self.pixel/2)*meterPerPixel)

		lon_bottomleft=self.add_meters_lon(lon,lat_bottom,-(self.pixel/2)*meterPerPixel)
		lon_bottomright=self.add_meters_lon(lon,lat_bottom,(self.pixel/2)*meterPerPixel)

		return [lat_upper,lat_upper,lat_bottom,lat_bottom],\
			[lon_upperleft,lon_upperright,lon_bottomleft,lon_bottomright]
