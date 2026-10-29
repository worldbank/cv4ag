'''
Get satellite data according to input file.
'''
from random import shuffle,random
import os,csv,json,sys
from PIL import Image
from utils import tiles
from utils.mapbox_static import MapboxStatic
from utils.naip import NaipTiles
from utils.coordinate_converter import CoordConvert
from modules.getFeatures import latLon,getBBox
from libs.foldernames import satDataFolder,testDataFolder,tilesfile,dataName

def get_satellite(inputFile,mapboxtoken=None,count=1000,zoomLevel=17,
	outputFolder='data',xpixel=480,ypixel=360,epsg=None,elements=None,
	randomImages=False,source='naip',year=2021):
	'''
	Get satellite data in order to input GIS information.

	Parameters:
	'inputFile': Input file (GeoJSON format or parsed into GeoJSON)
	'mapboxtoken': Access token for Mapbox (go to mapbox.com to create one)
	'count': Number of satellite images to be downloaded
	'zoomLevel': Zoom level (see libs/zoomLevel.csv for resolutions)
	'outputFolder': Folder to store output data in
	'xpixel': Number of pixels of satellite images (width)
	'ypixel': Number of pixels of satellite images (height)
	'epsg': EPSG code for coordinate system in GIS data (will try to find automatically
		if not provided)
	'elements': GIS data can also be input directly
	'randomImages': Get center of random polygons (False) or within Boundary Box of data (True)
	'source': 'naip' (USDA aerial imagery of the US, public domain) or 'mapbox'
	'year': Year of NAIP imagery
	'''
	if (not inputFile) and (not elements):
		print("Error: Provide input file.")
		sys.exit(1)
	if source=='mapbox':
		print("Warning: The Mapbox terms of service do not allow to train machine learning models\
			with Mapbox imagery or to download it in bulk.")
		if not mapboxtoken:
			print("Error: Provide mapbox token (more informations on www.mapbox.com).")
			sys.exit(1)
	elif source!='naip':
		print("Error: Unknown satellite source",source)
		sys.exit(1)

	# We need the elements
	if not elements:
		print('Loading %s...' % inputFile)
		with open(inputFile, 'r') as f:
			elements = json.load(f)

	#get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements,epsg)
	#create folders
	subpath=outputFolder+"/"+dataName(inputFile)
	for folder in [subpath,subpath+satDataFolder,subpath+testDataFolder]:
		if not os.path.isdir(folder):
			os.makedirs(folder)
			print('Directory',folder,'created')

	#Write metadata
	with open(subpath+satDataFolder+"meta.csv","a+") as f:
		f.write("ZoomLevel,,"+str(zoomLevel)+"\n")
	#Center of each tile, used by overlay to compute the exact image footprint
	tilesPath=subpath+satDataFolder+tilesfile
	knownTiles=set()
	if os.path.isfile(tilesPath):
		with open(tilesPath,newline='') as f:
			knownTiles={row['name'] for row in csv.DictReader(f)}
	else:
		with open(tilesPath,"w") as f:
			f.write("name,lon,lat,zoom,width,height\n")
	#bbox of the data
	xlist=[]
	ylist=[]
	for element in elements['features']:
		minxe,maxxe,minye,maxye=getBBox(element)
		xlist.append(minxe)
		xlist.append(maxxe)
		ylist.append(minye)
		ylist.append(maxye)
	minx=min(xlist)
	maxx=max(xlist)
	miny=min(ylist)
	maxy=max(ylist)

	if randomImages: #random locations, some of them may fail
		index_list = list(range(3*count))
	else:
		index_list = list(range(len(elements['features']))) #featue map
		# Randomize elements list to make sure we don't download all pics from the
		# same area
		shuffle(index_list)

	# Now we're gonna download the satellite images for these locations
	namespace= dataName(inputFile) #get input file name as namespace

	mapbox_static = MapboxStatic(
	    namespace=namespace,
	    root_folder=subpath+satDataFolder[0:-1])
	if source=='naip':
		corners=[myCoordConvert.convert(x,y) for x in (minx,maxx) for y in (miny,maxy)]
		naip=NaipTiles((min(c[0] for c in corners),min(c[1] for c in corners),
			max(c[0] for c in corners),max(c[1] for c in corners)),year)
		if len(naip)==0:
			print("Error: No NAIP imagery of",year,"for this area. NAIP covers the contiguous US,\
				each state every 2-3 years.")
			sys.exit(1)

	total_downloaded = 0
	print("------------------- Getting Satellite data -------------------")
	for c,i in enumerate(index_list):
		if randomImages:
			av_lon=minx+((maxx-minx)*random())
			av_lat=miny+((maxy-miny)*random())
			element_id_str=1000000+c #1000000 indicates random value
			with open(subpath+satDataFolder+"meta.csv","a+") as f:
				f.write(str(element_id_str)+","+str(av_lon)+","+str(av_lat)+"\n")
		else:
			element_id_str = i
			#figure out center of polygon
			av_lon,av_lat=latLon(elements['features'][i])
		#Convert to standard format
		longitude,latitude= myCoordConvert.convert(av_lon,av_lat)

		#get url
		print("Coordinates WSG84: "+str(longitude)+','+str(latitude))
		if (av_lon != longitude) and (av_lat != latitude):
			print("Coordinates Native: "+str(av_lon)+','+str(av_lat))
		if source=='naip':
			success = getNaipTile(naip,mapbox_static.get_filepath(element_id_str),
				longitude,latitude,zoomLevel,xpixel,ypixel)
		else:
			url = mapbox_static.get_url(
				latitude=latitude,
				longitude=longitude,
				mapbox_zoom=zoomLevel,
				access_token=mapboxtoken,
				width=xpixel,
				height=ypixel)
			#download data
			success = mapbox_static.download_tile(
			    element_id=element_id_str,
			    url=url,verbose=True)
		if success:
			name=os.path.split(mapbox_static.get_filepath(element_id_str))[-1]
			if name not in knownTiles:
				with open(tilesPath,"a") as f:
					f.write("%s,%.8f,%.8f,%d,%d,%d\n" %
						(name,longitude,latitude,zoomLevel,xpixel,ypixel))
				knownTiles.add(name)
			total_downloaded += 1
			print(total_downloaded,'/',count)
		if total_downloaded >= count:
			break

def getNaipTile(naip,filepath,longitude,latitude,zoomLevel,xpixel,ypixel,mincoverage=0.99):
	'''write the NAIP image of a tile, returns True if available'''
	if os.path.isfile(filepath):
		print('[naip] Tile already downloaded (%s).' % filepath)
		return True
	print('[naip] Reading tile (%s).' % filepath)
	image,coverage=naip.read(tiles.footprint(longitude,latitude,zoomLevel,xpixel,ypixel),
		xpixel,ypixel)
	if coverage<mincoverage:
		print('[naip] Skipping tile, only %.0f%% covered by imagery.' % (100*coverage))
		return False
	Image.fromarray(image).save(filepath)
	return True
