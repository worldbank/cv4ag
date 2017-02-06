#!usr/bin/python
'''
Overlay classes and satellite data
'''
import json
import os
import utils.gdal_rasterize as gdal_rasterize
from utils.coordinate_converter import CoordConvert
from utils.getImageCoordinates import imageCoordinates
from modules.getFeatures import latLon,find_between

# also requires gdal (ex


def overlay(outputFolder,inputFile,pixel=1280,zoomLevel=None):
	'''
	Overlays images in satiImageFolder
	with data in inputFile
	'''
	if not zoomLevel:
		print "Warning: Zoom level not set. Assuming zoom level 17."
		zoomLevel = 17

	#Get list of images
	samples_data = {}
	#set outputFolder to directory above the /sat directory
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]=="sat":
		outputFolder=outputFolder[0:-4]

	#load data and check if images in folder
	image_files = [f for f in os.listdir(outputFolder+"/sat") if f.endswith('.png') \
		and f.startswith(os.path.split(inputFile)[-1])] #has to be png image and start with input filename
	if len(image_files)==0:
		print "No images found in",outputFolder+"/sat"
		exit()
	else:
		print "Number of images found:",len(image_files)

	print 'Opening %s...' % inputFile
	with open(inputFile, 'r') as f:
		elements = json.load(f)
	#Get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements)
	#Get imageconverter
	myImageCoord=imageCoordinates(pixel,'libs/zoomLevelResolution.csv',zoomLevel)
	for image in image_files:
		# The index is between the last underscore and the extension dot
		index = int(find_between(image,"_",".png"))
		av_lat,av_lon=latLon(elements['features'][index]) # get center points
		#Convert to standard format
		if code != 4319: # if not already in wgs84 standard format
			latlon= myCoordConvert.convert(av_lat,av_lon)
			print latlon
			latitude=latlon[1]
			longitude=latlon[0]
		else: #if already in wgs84 format
			latitude= av_lat
			longitude= av_lot
		#Calculate image coordinates in WSG 84
		image_box_raw= myImageCoord.getImageCoord(latitude,longitude)
		print image_box_raw
		#Convert back to original format
		if code != 4319: # if not already in wgs84 standard format
			image_box=\
				myCoordConvert.convertBack(image_box_raw[1],image_box_raw[0])
			#	myCoordConvert.convertBack(108.,16.)
		else:
			image_box=image_box_raw
		image_box_x = image_box[1]
		image_box_y = image_box[0]	
		print image_box
		print image_box_x,image_box_y

		#rasterize corresponding data
		print 'Converting %s...' % inputFile
		tifile=outputFolder+"/"+os.path.split(inputFile)[-1][0:-5]+".tif" #path for raster tif file
		try:
			os.remove(tifile)
		except OSError:
			pass
		open(tifile,'a+').close() #create file if it does not exist
		gdal_rasterize.rasterize(	\
			inputFile,
			tifile,
			ts=[500,500],
			tr=[1,1])

		
	
	# We need the elements from inputFile
	#with open(inputFile, 'r') as f:
	#	elements = json.load(f)
