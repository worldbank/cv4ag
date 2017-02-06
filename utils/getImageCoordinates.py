
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
	
	def getImageCoord(self,av_lat,av_lon):
		''' Get 4 corners of image in wsg84 format '''
		print toMeter(15)
		
