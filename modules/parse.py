import os,csv,sys
import geopandas as gpd
import pyogrio

from modules import get_stats

def parse(inputFile=None,outputFolder="data",\
	outputFile="datatiles.json",datatype=None,top=15,layernumber=None,key='Descriptio',\
	scriptFile=None, scriptArg1=None,scriptArg2=None,\
	scriptArg3=None,scriptArg4=None):
	"""
	Acquire and parse data into GeoJSON

	Parameters:
	'inputFile': Filename for input data
	'outputFolder': Filename for output data
	'datatype': Data type (will find automatically if not given)
	'top': The N most frequent classes in the GIS file to be processed.
	'layernumber': The layer ID of the layer to be processed, when input file contains multiple layers
	'key': Keyword in 'properties' of GIS file to classify for.
	'script': Script that returns input data. Has to contain script(.) function that returns the filename of the output file (of course, scripts can be run outside of this framework)
	'scriptArgN': Arguments for script, if any

	Return:
	'outputFile': Output file name of the converted file, if input file not GeoJSON
	'stats': Labels for most frequent classes
	'freq': Frequency of most frequent classes
	'elements': GeoJSON data
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
		scriptArgs=[arg for arg in [scriptArg1,scriptArg2,scriptArg3,scriptArg4] if arg]
		scriptReturn = scriptModule.script(*scriptArgs)
		# parse returns
		inputFile = 	scriptReturn[0]
		datatype =	scriptReturn[1]
		print("Script to get tile data executed successfully within \'parse\'")
	else:
		if inputFile == None:
			print("Error: provide either script or input file")
			sys.exit(1)

	#check if provided code exists and if it is ogr-readable vector or
	#ogr-readable raster format
	vector_or_raster=0 # 2 = Vector, 1 = Raster
	if datatype: #if raster format has to be polygonized into vector format
		with open('libs/ogr_raster_formats.csv',newline='') as csvfile:
			raster_formats = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
		for cnt in range(0,len(raster_formats)):
			if datatype == raster_formats[cnt][1]:
				print("Detected format:",raster_formats[cnt][0])
				print("This format is a raster format")
				vector_or_raster = 1
		with open('libs/ogr_vector_formats.csv',newline='') as csvfile:
			vector_formats = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
		for cnt in range(0,len(vector_formats)):
			if datatype == vector_formats[cnt][1]:
				print("Detected format:",vector_formats[cnt][0])
				print("This format is a vector format")
				vector_or_raster = 2
		if vector_or_raster == 0:
			print("Error: Format",datatype,\
				"not found. Check libs/*.csv for available formats.")
			sys.exit(1)
	if vector_or_raster == 0:
		vector_or_raster = 2 # Assuming vector format if no datatype specified.
	# Remove slash if it is at the end of input file
	if inputFile[-1]=="/":
		inputFile=inputFile[0:-1]
	stats=freq=elements=None
	if datatype=="GeoJSON" or inputFile.endswith("json"):
		outputFile=inputFile#ignore, if already in GeoJSON format
		print("No parsing needed")
		stats,freq,elements=get_stats.get_stats(outputFile,top,key=key)
	elif vector_or_raster == 1: #vectorize raster format
		outputFile=overwrite(outputFolder+"/"+os.path.split(inputFile)[-1]+".json")
		print("Polygonizing raster...")
		polygonize(inputFile,outputFile,key)
		print("Converted to",outputFile)
		stats,freq,elements=get_stats.get_stats(outputFile,top,key=key)
	else:
		#get layers of input file
		pyogrio.set_gdal_config_options({'OSM_USE_CUSTOM_INDEXING':'NO'})
		layers = [layer[0] for layer in pyogrio.list_layers(inputFile)]
		if len(layers)>1:
			# Select layers (one or all)
			if not layernumber:
				for i,layer in enumerate(layers):
					print(i+1,"-",layer)
				choseLayer = int(input(\
					"Multiple layers found. Chose layer (number) or \'0\' for all layers: "))
			else:
				choseLayer = layernumber
			if choseLayer==0: # iterate over each layer
				for i in range(0,len(layers)):
					#create filename
					print("Converting layer",layers[i],"(",i+1,"out of",len(layers),"layers)...")
					_,outputFile=os.path.split(inputFile+str(i+1)+".json")
					outputFile=overwrite(outputFolder+"/"+outputFile)
					convert(inputFile,outputFile,layers[i])
					print("Converted to",outputFile)
					stats,freq,_=get_stats.get_stats(outputFile,top,key=key) #get statistics
					elements=None
			else: #only convert one layer
				_,outputFile=os.path.split(inputFile+str(choseLayer)+".json")
				print("Converting layer",layers[choseLayer-1],"...")
				outputFile=overwrite(outputFolder+"/"+outputFile)
				convert(inputFile,outputFile,layers[choseLayer-1])
				print("Converted to",outputFile)
				stats,freq,elements=get_stats.get_stats(outputFile,top,key=key) #get statistics
		else:
			_,outputFile=os.path.split(inputFile+".json")
			print("Converting...")
			outputFile=overwrite(outputFolder+"/"+outputFile)
			convert(inputFile,outputFile)
			print("Converted to",outputFile)
			stats,freq,elements=get_stats.get_stats(outputFile,top,key=key) #get statistics
	return outputFile,stats,freq,elements

def convert(inputFile,outputFile,layer=None):
	'''convert a vector layer to GeoJSON, keeping its coordinate system'''
	gpd.read_file(inputFile,layer=layer).to_file(outputFile,driver="GeoJSON")

def polygonize(inputFile,outputFile,key):
	'''convert a raster with class values to GeoJSON polygons with the value in key'''
	import rasterio
	from rasterio.features import shapes
	from shapely.geometry import shape
	with rasterio.open(inputFile) as src:
		band=src.read(1)
		mask=band!=src.nodata if src.nodata is not None else None
		polygons=[(shape(geometry),value) for geometry,value in \
			shapes(band,mask=mask,transform=src.transform)]
		crs=src.crs
	gpd.GeoDataFrame({key:[str(int(v)) for _,v in polygons]},
		geometry=[p for p,_ in polygons],crs=crs).to_file(outputFile,driver="GeoJSON")

def overwrite(outputFile,promptoverwrite=False):
	'''remove file if already exists. necessary as GeoJSON engine cannot
	overwrite files'''
	try:
		if os.path.exists(outputFile):
			if promptoverwrite:
				overwrite_answer=input(outputFile+" already exists. Overwrite? (y/n) ")
			else:
				overwrite_answer=''
			if overwrite_answer=="y" or (not promptoverwrite):
				os.remove(outputFile)
			else:
				outputFile=input("Provide alternative filename: ")
	except OSError:
		pass
	return outputFile
