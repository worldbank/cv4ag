'''
Get satellite data according to input file.
'''
from random import shuffle,random
import os,csv,json,sys
from utils.mapbox_static import MapboxStatic
from utils.coordinate_converter import CoordConvert
from modules.getFeatures import latLon,getBBox
from libs.foldernames import satDataFolder,testDataFolder,tilesfile,dataName

def get_satellite(inputFile,mapboxtoken=None,count=1000,zoomLevel=17,
	outputFolder='data',xpixel=480,ypixel=360,epsg=None,elements=None,
	randomImages=False):
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
	'''
	if (not inputFile) and (not elements):
		print("Error: Provide input file.")
		sys.exit(1)
	if not mapboxtoken:
		print("Error: Provide mapbox token (more informations on www.mapbox.com).")
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
	#get bbox if set to random
	if randomImages:
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

	index_list = list(range(len(elements['features']))) #featue map
	# Randomize elements list to make sure we don't download all pics from the
	# same area
	shuffle(index_list)

	# Now we're gonna download the satellite images for these locations
	namespace= dataName(inputFile) #get input file name as namespace

	mapbox_static = MapboxStatic(
	    namespace=namespace,
	    root_folder=subpath+satDataFolder[0:-1])

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
