#!usr/bin/python
'''
Overlay classes and satellite data
'''
import json
import os


def overlay(outputFolder,inputFile):
	'''
	Overlays images in satiImageFolder
	with data in inputFile
	'''
	# We need the elements from inputFile
	print 'Loading %s...' % inputFile
	with open(inputFile, 'r') as f:
		elements = json.load(f)

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
		print len(image_files)
