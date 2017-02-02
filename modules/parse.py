#!usr/bin/python
from osgeo import gdal
import utils.ogr2ogr as ogr2ogr
import utils.ogrinfo as ogrinfo
import utils.gdal_polygonize_edited as gdal_polygonize
import get_stats
import os,csv
import json

def parse(inputFile=None,outputFolder="data",\
	outputFile="datatiles.json",datatype=None,\
	scriptFile=None, scriptArg1=None,scriptArg2=None,\
	scriptArg3=None,scriptArg4=None):
	"""
	Acquire and parse data
	
	'datatype': Data type (json or geoTiff)
	'outputFolder': Filename for output data
	'inputFile': Filename for input data
	'script': Script that returns input data. Has to contain script(.) function that returns the filename of the output file (of course, scripts can be run outside of this framework)
	'scriptArg': Arguments for script, if any
	"""
	#Execute script, if given. This should allow to users to load data from 
	#custom scripts.
	if scriptFile:
		# import script file as module for input with and without .py ending
		if scriptFile[0:8] == "scripts/":
			scriptFile = scriptFile[8:] # delete folder if present
		if scriptFile[-3:] == ".py":
			scriptFile = scriptFile[0:-3] # delete .py ending if present
		scriptModule = __import__(scriptFile)
		
		#load according to how many arguments are given
		if scriptArg1:
			if scriptArg2:
				if scriptArg3:
					if scriptArg4:
						scriptReturn= scriptModule.script(scriptArg1,scriptArg2,scriptArg3,scriptArg4)
					else:
						scriptReturn= scriptModule.script(scriptArg1,scriptArg2,scriptArg3)
				else:
					scriptReturn= scriptModule.script(scriptArg1,scriptArg2)
			else:
				scriptReturn= scriptModule.script(scriptArg1)
		else:
			scriptReturn = scriptModule.script()
		# parse returns
		inputFile = 	scriptReturn[0]
		datatype =	scriptReturn[1]
		print "Script to get tile data executed successfully within \'parse\'"
	else:
		if inputFile == None:
			print "Error: provide either script or input file"
			exit()

	#check if provided code exists and if it is ogr-readable vector or 
	#ogr-readable raster format
	vector_or_raster=0 # 2 = Vector, 1 = Raster
	if datatype: #if raster format has to be polygonized into vector format
		with open('libs/ogr_raster_formats.csv','rb') as csvfile:
			raster_formats = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
		for cnt in range(0,len(raster_formats)):
			if datatype == raster_formats[cnt][1]:
				print "Detected format:",raster_formats[cnt][0]
				if raster_formats[cnt][-1]!='Yes':
					print "Please be aware:"
					print "Is format compiled in standard GDAL?",raster_formats[cnt][-1]
				print "Ths format  is a raster format"
				vector_or_raster = 1
		with open('libs/ogr_vector_formats.csv','rb') as csvfile:
			vector_formats = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
		for cnt in range(0,len(vector_formats)):
			if datatype == vector_formats[cnt][1]:
				print "Detected format:",vector_formats[cnt][0]
				if vector_formats[cnt][-1]!='Yes':
					print "Please be aware:"
					print "Is format compiled in standard GDAL?",vector_formats[cnt][-1]
				print "This format is a vector format"
				vector_or_raster = 2
		if vector_or_raster == 0:
			print "Error: Format",datatype,\
				"not found. Check libs/*.csv for available formats."
			exit()
	if vector_or_raster == 0:
		vector_or_raster = 2 # Assuming vector format if no datatype specified.
	# mitigate index error if length of json file name >=4 characters
	if len(inputFile)>=4:
		inputFileCopy=inputFile
	else:
		inputFileCopy="      "
	if datatype=="GeoJSON" or inputFileCopy[-5:]==".json":
			outputFile=inputFile#ignore, if already in GeoJSON format
			print "No parsing needed"
			get_stats.get_stats(outputFile)
	else:
		#vectorize if in raster format and user agrees
		if vector_or_raster == 1:
			if input("Your file is a raster format. Convert to vector format? (y/n)").lower == "y":
				gdal_polygonize.polygonize(inputFile,outputFolder+"/polygonised.json",
					"GeoJSON",quiet_flag=0) #not tested
				inputFile=outputFolder+"/polygonised.json"
		#get layers of input file
		layers = ogrinfo.main(["-so",inputFile])
		if len(layers)>1:
			# Select layers (one or all)
			choseLayer = input("Multiple layers found. Chose layer (number) or \'0\' for all layers: ")
			if choseLayer==0: # iterate over each layer
				for i in range(0,len(layers)):
					print "Converting layer",layers[i],"(",i+1,"out of",len(layers),"layers)..."
					# avoid GeoJSON error (GeoJSON cannot overwrite files)
					_,outputFile=os.path.split(inputFile+str(i+1)+".json")
					outputFile=outputFolder+"/"+outputFile
					try:
						os.remove(outputFile)
					except OSError:
						pass	
					ogr2ogr.main(["","-f","GeoJSON",outputFile,inputFile,layers[i]]) #convert layer
					print ''
					print "Converted to",outputFile
					get_stats.get_stats(outputFile)
			else: #only convert one layer
				_,outputFile=os.path.split(inputFile+".json")
				outputFile=outputFolder+"/"+outputFile
				print "Converting layer",layers[choseLayer-1],"..."
				try:
					os.remove(outputFile)
				except OSError:
					pass	
				ogr2ogr.main(["","-f","GeoJSON",outputFile,inputFile,layers[choseLayer-1]]) #convert layer
				print ''
				print "Converted to",outputFile
				get_stats.get_stats(outputFile)
		else:
			_,outputFile=os.path.split(inputFile+".json")
			outputFile=outputFolder+"/"+outputFile
			print "Converting..."
			ogr2ogr.main(["","-f","GeoJSON",outputFile,inputFile]) #convert layer
			print ''
			print "Converted to",outputFile
			get_stats.get_stats(outputFile)
	return outputFolder+"/"+outputFile
