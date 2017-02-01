from osgeo import gdal
import utils.ogr2ogr as ogr2ogr
import utils.gdal_polygonize_edited as gdal_polygonize
import os,csv
import json

def parse(inputFile=None,outputFolder="data",datatype=None,\
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

	#check if provided code exists and if it is vector or raster format
	vector_or_raster=0 # 2 = Vector, 1 = Raster
	with open('libs/ogr_raster_formats.csv','rb') as csvfile:
		raster_formats = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
	for cnt in range(0,len(raster_formats)):
		if datatype == raster_formats[cnt][1]:
			print "Detected format:",raster_formats[cnt][0]
			if raster_formats[cnt][-1]!='Yes':
				print "Please be aware:"
				print "Is format compiled in standard GDAL?",raster_formats[cnt][-1]
			print "This format is a raster format"
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

	#ignore, if already in GeoJSON format
	if datatype=="GeoJSON":
		pass
	else:
		#vectorize if in raster format
		if vector_or_raster == 2:
			pass
		elif vector_or_raster == 1:
			gdal_polygonize.polygonize(inputFile,outputFolder+"/"+"polygonised.json",
				"GeoJSON",quiet_flag=0)
			
			


	#rawData = open(inputFile,'r')
		

	#Parse to json, if elements are not json

	#Save	
	#with open(outputFolder+"datatiles.json", 'w') as f:
	#	json.dump(datatiles,f)
	#print "Written to "+outputFolder+"datatiles.json"
