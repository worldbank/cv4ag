'''
Overlay classes and satellite data
'''
import os,csv,json,math,sys
import numpy as np
import geopandas as gpd
from PIL import Image
from rasterio.features import rasterize
from rasterio.transform import from_bounds
from shapely.geometry import box,shape
from utils import tiles
from utils.coordinate_converter import CoordConvert
from modules.getFeatures import latLon,find_between
from modules.get_stats import get_stats
from libs.colorlist import colorlist
from libs.foldernames import *

def loadFeatures(elements,stats,key,code):
	'''
	GeoDataFrame with the features of the classes in stats and their class id
	(1 = most frequent class, 0 is background). Reprojected to Web Mercator,
	the projection of the satellite images.
	'''
	classes={name:i+1 for i,name in enumerate(stats)}
	geometries=[]
	classids=[]
	for feature in elements['features']:
		classid=classes.get(str(feature['properties'].get(key)))
		if classid and feature.get('geometry'):
			geometries.append(shape(feature['geometry']))
			classids.append(classid)
	features=gpd.GeoDataFrame({'classid':classids},geometry=geometries,
		crs='EPSG:'+str(code)).to_crs(tiles.MERCATOR_CRS)
	# less frequent classes are drawn on top of more frequent ones
	return features.sort_values('classid',kind='stable').reset_index(drop=True)

def readTileMeta(sat):
	'''centers and zoom levels of downloaded tiles, written by get_satellite'''
	tileMeta={}
	if os.path.isfile(sat+tilesfile):
		with open(sat+tilesfile,newline='') as f:
			for row in csv.DictReader(f):
				tileMeta[row['name']]=row
	return tileMeta

def tileCenter(image,sat,elements,myCoordConvert,randomImages):
	'''
	WGS84 center of a tile downloaded before tiles.csv was written: center of the
	feature in the file name or, for random tiles, the coordinates in meta.csv
	'''
	index = int(find_between(image,"_",".png"))
	av_lon=None
	if randomImages:
		with open(sat+"meta.csv",newline='') as csvfile:
			for coord in csv.reader(csvfile,delimiter=",",quotechar='"'):
				if coord[0]==str(index):
					av_lon=float(coord[1])
					av_lat=float(coord[2])
					break
	if av_lon is None:
		av_lon,av_lat=latLon(elements['features'][index]) # get center points
	return myCoordConvert.convert(av_lon,av_lat)

def shiftBounds(bounds,lonshift,latshift,shiftformat,lat=0):
	'''
	shift the label window. shiftformat 0: fraction of the image,
	1: meters on the ground
	'''
	west,south,east,north=bounds
	if shiftformat == 0:
		lonshift=lonshift*(east-west)
		latshift=latshift*(north-south)
	else: # Web Mercator units are stretched by 1/cos(latitude)
		lonshift=lonshift/math.cos(math.radians(lat))
		latshift=latshift/math.cos(math.radians(lat))
	return (west-lonshift,south-latshift,east-lonshift,north-latshift)

def rasterLabels(features,bounds,width,height):
	'''label image with class ids of the features within bounds'''
	idx=np.sort(features.sindex.query(box(*bounds),predicate='intersects'))
	if len(idx)==0:
		return np.zeros((height,width),dtype=np.uint8)
	selected=features.iloc[idx]
	return rasterize(zip(selected.geometry,selected.classid.astype(int)),
		out_shape=(height,width),
		transform=from_bounds(*bounds,width,height),
		fill=0,dtype='uint8')

def checkImage(satImage,label):
	'''satellite image with class colors blended in, for visual checks'''
	out=np.asarray(satImage.convert('RGB'),dtype=np.float32).copy()
	for classid in np.unique(label):
		if classid==0:
			continue
		try:
			r,g,b,a=colorlist[classid-1]
		except IndexError:
			print("Warning: Color list for visual check file too short")
			continue
		mask=label==classid
		alpha=a/255.
		out[mask]=(1-alpha)*out[mask]+alpha*np.array([r,g,b],dtype=np.float32)
	return Image.fromarray(out.astype(np.uint8))

def writeFootprints(path,footprints):
	with open(path,"w") as f:
		f.write("name,crs,west,south,east,north\n")
		for name in sorted(footprints):
			crs,bounds=footprints[name]
			f.write(name+","+crs+","+",".join("%.4f" % v for v in bounds)+"\n")

def readFootprints(path):
	footprints={}
	if os.path.isfile(path):
		with open(path,newline='') as f:
			for row in csv.DictReader(f):
				footprints[row['name']]=(row['crs'],tuple(float(row[k])\
					for k in ['west','south','east','north']))
	return footprints

def overlay(outputFolder,inputFile,xpixel=480,ypixel=360,zoomLevel=None,lonshift=0,latshift=0,
	shiftformat=1,top=10,stats=None,count=None,key='Descriptio',epsg=None,
	elements=None,randomImages=False,sat=None):
	'''
	Overlays images in satiImageFolder
	with data in inputFile
	'''

	if not zoomLevel:
		print("Warning: Zoom level not set. Assuming zoom level 17.")
		zoomLevel = 17

	outputFolder=stripSatFolder(outputFolder)

	#Make directory for subfiles
	subpath=outputFolder+"/"+dataName(inputFile)
	for subsubpath in ['',trainingDataFolder,checkDataFolder,testDataFolder]:
		if not os.path.isdir(subpath+subsubpath):
			os.makedirs(subpath+subsubpath)
			print('Directory',subpath+subsubpath,'created')

	#load data and check if images in folder
	#has to be png image and start with input filename
	if sat: #if sat folder externally provided
		sat = sat+'/'
	else:
		sat = subpath+satDataFolder
	listImages=sorted(os.listdir(sat))
	image_files = [f for f in listImages if f.endswith('.png') \
		and f.startswith(dataName(inputFile))]
	if len(image_files)==0:
		print("Error: No images found in",sat[0:-1])
		sys.exit(1)
	print("Number of images found:",len(image_files))
	if count:
		image_files=image_files[:count]
	print("Create",len(image_files),"images")

	print('Get GIS elements...')
	if not elements:
		print('Opening %s...' % inputFile)
		with open(inputFile, 'r') as f:
			elements = json.load(f)
	#Get statistics if not in input
	if not stats:
		stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
			elements=elements)
	else:
		freq=None
	if len(stats)==0:
		print("No features found.")

	#Get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements,epsg)
	print("Reproject features...")
	features=loadFeatures(elements,stats,key,code)
	print(len(features),"features of",len(stats),"classes")
	tileMeta=readTileMeta(sat)
	footprintPath=subpath+trainingDataFolder+footprintsfile
	footprints=readFootprints(footprintPath)

	for cnt,image in enumerate(image_files):
		print('')
		print(str(cnt+1)+'/'+str(len(image_files)))
		satImage=Image.open(sat+image)
		width,height=satImage.size
		#Image footprint in Web Mercator
		if image in tileMeta:
			meta=tileMeta[image]
			longitude,latitude=float(meta['lon']),float(meta['lat'])
			bounds=tiles.footprint(longitude,latitude,int(meta['zoom']),
				int(meta['width']),int(meta['height']))
		else: # downloaded before tiles.csv existed
			longitude,latitude=tileCenter(image,sat,elements,myCoordConvert,randomImages)
			bounds=tiles.footprint(longitude,latitude,zoomLevel,width,height)
		print("Coordinates WSG84: "+str(longitude)+','+str(latitude))
		if lonshift or latshift:
			bounds=shiftBounds(bounds,lonshift,latshift,shiftformat,latitude)
			print("Shift applied:",lonshift,latshift)

		tifile=subpath+trainingDataFolder+image[0:-4]+"train.png" #path for label file
		print('Converting',image,'to',os.path.split(tifile)[-1])
		label=rasterLabels(features,bounds,width,height)
		Image.fromarray(label,mode='L').save(tifile)
		footprints[image]=(tiles.MERCATOR_CRS,bounds)

		#Create test images for visual checks
		checkfile=subpath+checkDataFolder+image[0:-4]+"check.png" #path for check files
		checkImage(satImage,label).save(checkfile)
		print("Class label image",tifile," and check image created.")
		print("Labelled pixels:",'%.1f%%' % (100.*np.count_nonzero(label)/label.size))

	writeFootprints(footprintPath,footprints)
	print("Overlaying done.")
	return stats,freq
