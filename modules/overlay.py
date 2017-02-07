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
# find all features, create files only with feature,convert all to different band,merge
def overlay(outputFolder,inputFile,pixel=1280,zoomLevel=None,lonshift=0,latshift=0,
	shiftformat=0):
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
	#Create json-file for each layer
	#Get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements)
	#Get imageconverter
	myImageCoord=imageCoordinates(pixel,'libs/zoomLevelResolution.csv',zoomLevel)
	av_lats=[]
	av_lons=[]
	cnt = 1

	for image in image_files:
		# The index is between the last underscore and the extension dot
		index = int(find_between(image,"_",".png"))
		av_lat,av_lon=latLon(elements['features'][index]) # get center points
		print "Coordinates Native: "+str(av_lon)+','+str(av_lat)
		#Convert to standard format
		if code != 4319: # if not already in wgs84 standard format
			lotlan= myCoordConvert.convert(av_lon,av_lat)
			longitude=lotlan[0]
			latitude=lotlan[1]
		else: #if already in wgs84 format
			latitude= av_lat
			longitude= av_lot
		print "Coordinates WSG84: "+str(longitude)+','+str(latitude)
		#Calculate image coordinates in WSG 84
		image_box_lat,image_box_lon= myImageCoord.getImageCoord(latitude,longitude)
		#print 'Coordinates:',latitude,longitude
		#Convert back to original format
		if code != 4319: # if not already in wgs84 standard format
			image_box=\
				myCoordConvert.convertBack(image_box_lon,image_box_lat)
		else:
			image_box=image_box_raw
		image_lat = image_box[1]
		image_lon = image_box[0]	
		print "Coordinates Native corner: "+str(image_lat[0])+','+str(image_lon[0])
		print "Coordinates WSG84 corner: "+str(image_box_lon[0])+','+str(image_box_lat[0])

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
		#shift factor
		west=(image_lon[0]+image_lon[2])/2
		south=min(image_lat)
		east=(image_lon[1]+image_lon[3])/2
		north=max(image_lat)
		if shiftformat == 0:					#if fraction as shift unit
			lonshift_calc=lonshift*abs(east-west)
			latshift_calc=latshift*abs(north-south)
		else:
			lonshift_calc=lonshift
			latshift_calc=latshift
		print "Shift applied:"
		print "Longitudinal \t",lonshift_calc
		print "Lateral \t",latshift_calc
		#set rasterize settings
		size=[pixel,pixel]
		te=[west-lonshift_calc,south-latshift_calc,\
			east-lonshift_calc,north-latshift_calc] #image bounderies 
		print "Image bounderies:"
		print str(image_box_lat[0])[:-5],'\t',str(image_box_lon[0])[:-5],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lat[1])[:-5],'\t',str(image_box_lon[1])[:-5]
		print '\t|\t\t\t\t\t\t\t\t\t\t|\t'
		print '\t|\t\t\t\t\t\t\t\t\t\t|\t'
		print str(image_box_lat[2])[:-5],'\t',str(image_box_lon[2])[:-5],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lat[3])[:-5],'\t',str(image_box_lon[3])[:-5]
		
		#rasterize
		gdal_rasterize.rasterize(	\
			inputFile,
			tifile,
			ts=size,		# set resolution
			out_format='PNG',
			init=0,
			te=te,
			burn_values=[200])				# set image limits in te

		#Create test images for visual checks
		checkfile=outputFolder+checkDataFolder+os.path.split(image)[-1][0:-4]+"check.png" #path for check files
		if not os.path.isdir(outputFolder+checkDataFolder):
		    try:
			os.mkdir(outputFolder+checkDataFolder)
			print 'Training data folder created: %s' \
			    % outputFolder+checkDataFolder
		    except Exception as e:
			print 'Failed to create the check datafolder' 
		try:
			os.remove(checkfile)
		except OSError:
			pass
		background = Image.open(outputFolder+'/sat/'+image)
		foreground = Image.open(tifile)
		background.paste(foreground, (0, 0), foreground)
		background.save(checkfile)

	#Remove aux-files
#	try:
#		os.remove(outputFolder+trainingDataFolder+"*.aux.xml")
#	except OSError:
#		pass
