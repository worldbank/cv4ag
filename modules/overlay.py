#!usr/bin/python
'''
Overlay classes and satellite data
'''
import json
import os
from PIL import Image
import utils.gdal_rasterize as gdal_rasterize
from utils.coordinate_converter import CoordConvert
from utils.getImageCoordinates import imageCoordinates
from modules.getFeatures import latLon,find_between

trainingDataFolder="/train/"
checkDataFolder="/check/"

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
	av_lats=[]
	av_lons=[]
	#for index in range(0,len(elements['features'])):
	#	try:
	#		av_lat,av_lon=latLon(elements['features'][index]) # get center points
	#	except IndexError:
	#		pass
	#	av_lats.append(av_lat)
	#	av_lons.append(av_lon)
	cnt = 1
	for image in image_files:
		# The index is between the last underscore and the extension dot
		index = int(find_between(image,"_",".png"))
		av_lat,av_lon=latLon(elements['features'][index]) # get center points
		#Convert to standard format
		if code != 4319: # if not already in wgs84 standard format
			latlon= myCoordConvert.convert(av_lon,av_lat)
			longitude=latlon[0]
			latitude=latlon[1]
		else: #if already in wgs84 format
			latitude= av_lat
			longitude= av_lot
		#Calculate image coordinates in WSG 84
		image_box_lat,image_box_lon= myImageCoord.getImageCoord(latitude,longitude)
		#print 'Coordinates:',latitude,longitude
		#Convert back to original format
		if code != 4319: # if not already in wgs84 standard format
			image_box=\
				myCoordConvert.convertBack(image_box_raw[0],image_box_raw[1])
		else:
			image_box=image_box_raw
		print image_box
		image_lon = image_box[1]
		image_lat = image_box[0]	

		#rasterize corresponding data
		tifile=outputFolder+trainingDataFolder+os.path.split(image)[-1][0:-4]+"train.png" #path for raster tif file
		print str(cnt)+'/'+str(len(image_files))
		cnt+=1
		print 'Converting',image,'to',os.path.split(tifile)[-1]
		if not os.path.isdir(outputFolder+trainingDataFolder):
		    try:
			os.mkdir(outputFolder+trainingDataFolder)
			print 'Training data folder created: %s' \
			    % outputFolder+trainingDataFolder
		    except Exception as e:
			print 'Failed to create the training datafolder' 
		try:
			os.remove(tifile)
			os.remove(tifile+"*")
		except OSError:
			pass
		#set rasterize settings
		size=[pixel,pixel]
		te=[min(image_lon),min(image_lat),\
				max(image_lon),max(image_lat)]
		print "Image bounderies:"
		print str(image_box_lat[0])[:-7],'\t',str(image_box_lon[0])[:-7],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lat[1])[:-7],'\t',str(image_box_lon[1])[:-7]
		print '\t|\t\t\t\t\t\t\t\t|\t'
		print '\t|\t\t\t\t\t\t\t\t|\t'
		print str(image_box_lat[2])[:-7],'\t',str(image_box_lon[2])[:-7],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lat[3])[:-7],'\t',str(image_box_lon[3])[:-7]
		print te	
		#print size,te
		#rasterize
		gdal_rasterize.rasterize(	\
			inputFile,
			tifile,
			ts=size,		# set resolution
			out_format='PNG',
			init=0,
			te=te,
			burn_values=[200])				# set image limits in te

		#Create test images more visual checks
		checkfile=outputFolder+checkDataFolder+os.path.split(image)[-1][0:-4]+"check.png" #path for raster tif file
		if not os.path.isdir(outputFolder+checkDataFolder):
		    try:
			os.mkdir(outputFolder+checkDataFolder)
			print 'Training data folder created: %s' \
			    % outputFolder+checkDataFolder
		    except Exception as e:
			print 'Failed to create the check datafolder' 
		try:
			os.remove(tifile)
			os.remove(tifile+'*')
		except OSError:
			pass
	#	background = Image.open(outputFolder+'/sat/'+image)
	#	foreground = Image.open(tifile)

	#	background.paste(foreground, (0, 0), foreground)
	#	background.save(checkfile)
	#Remove aux-files
	try:
		os.remove(outputFolder+trainingDataFolder+"*.aux.xml")
	except OSError:
		pass
	# We need the elements from inputFile
	#with open(inputFile, 'r') as f:
	#	elements = json.load(f)
