#!usr/bin/python
'''
Overlay classes and satellite data
'''
import json
import os
import utils.gdal_rasterize as gdal_rasterize
# also requires gdal (ex

def find_between( s, first, last ):
	'''find substrings. used to get index out of image filename'''
	try:
	    start = s.rindex( first ) + len( first )
	    end = s.rindex( last, start )
	    return s[start:end]
	except ValueError:
	    return ""

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
	for image in image_files:
		# The index is between the last underscore and the extension dot
		# For example: pitch_volleyball_268478401.png -> 268478401
		index = find_between(image,"_",".png")
		print image,index

	#	element	

	#rasterize data
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
