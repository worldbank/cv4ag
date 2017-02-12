#!usr/bin/python
'''
Get satellite data according to input file.
'''
from random import shuffle,random
from utils.mapbox_static import MapboxStatic
from utils.coordinate_converter import CoordConvert
from modules.getFeatures import latLon,getBBox
from libs.foldernames import satDataFolder,testDataFolder
import os,json
def get_satellite(inputFile,mapboxtoken=None,count=1000,zoomLevel=17,
	outputFolder='data',xpixel=480,ypixel=360,epsg=None,elements=None,
	randomImages=False):
	if not inputFile:
		print "Error: Provide input file."
		exit()
	if not mapboxtoken:
		print "Error: Provide mapbox token (more informations on www.mapbox.com)."
		exit()
	#parser.add_argument('--sport',
	 #   type=str, default='baseball',
	  #  help='Sport tag, for example: baseball, tennis, or soccer.')

	# We need the elements
	if not elements:
		print 'Loading %s...' % inputFile
		with open(inputFile, 'r') as f:
			elements = json.load(f)

	#get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements,epsg)
	#create folders
	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	if not os.path.isdir(subpath):
		os.mkdir(subpath)
		print 'Directory',subpath,'created'
	if not os.path.isdir(subpath+satDataFolder):
		os.mkdir(subpath+satDataFolder)
		print 'Directory',subpath+satDataFolder,'created'
	if not os.path.isdir(subpath+testDataFolder):
		os.mkdir(subpath+testDataFolder)
		print 'Directory',subpath+testDataFolder,'created'
	
	#Write metadata
	with open(subpath+satDataFolder+"meta.csv","a+") as f:
		f.write("ZoomLevel,,"+str(zoomLevel))

	#get bbox if set to random
	if randomImages:
		xlist=[]
		ylist=[]
		for element in elements:
			minxe,maxxe,minye,maxye=getBBox(element)
			xlist.append(minxe)
			xlist.append(maxxe)
			ylist.append(minye)
			ylist.append(maye)
		minx=min(xlist)
		maxx=max(xlist)
		miny=min(ylist)
		maxy=max(ylist)
	else:
		element_list = []
		index_list = range(len(elements['features'])) #featue map
		# Randomize elements list to make sure we don't download all pics from the
		shuffle(index_list)
		for i in index_list:
			element_list.append(elements['features'][i]) #feature map

	# Now we're gonna download the satellite images for these locations
	namespace= os.path.split(inputFile)[-1][:-5] #get input file name as namespace

	mapbox_static = MapboxStatic(
	    namespace=namespace,
	    root_folder=subpath+satDataFolder[0:-1])

	total_downloaded = 0
	c = 0
	print "------------------- Getting Satellite data -------------------"
	for element in element_list:
		if randomImages:
			randomValue=random()
			av_lon=minx+((maxx-minx)*randomValue)
			av_lat=miny+((maxy-miny)*randomValue)
			element_id_str=1000000+c #1000000 indicates random value
			with open(subpath+satDataFolder+"meta.csv","w+") as f:
				f.write(element_id_str+","+av_lon+","+av_lat)
		else:
			element_id_str = index_list[c]
			#figure out center of polygon
			av_lon,av_lat=latLon(element)
		#Convert to standard format
		if code != 4319: # if not already in wgs84 standard format
			lotlan= myCoordConvert.convert(av_lon,av_lat)
			longitude=lotlan[0]
			latitude=lotlan[1]
		else: #if already in wgs84 format
			latitude= av_lat
			longitude= av_lon
					
		#get url
		print "Coordinates WSG64: "+str(longitude)+','+str(latitude)
		if (av_lon != longitude) and (av_lat != latitude):
			print "Coordinates Native: "+str(av_lon)+','+str(av_lat)
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
			total_downloaded += 1
			print total_downloaded,'/',count
		c += 1
		if total_downloaded >= count:
			break
