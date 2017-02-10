#!usr/bin/python
'''
Get satellite data according to input file.
'''
from random import shuffle
from utils.mapbox_static import MapboxStatic
from utils.coordinate_converter import CoordConvert
from modules.getFeatures import latLon
from libs.foldernames import satDataFolder
import os,json
def get_satellite(inputFile,mapboxtoken=None,count=1000,zoomLevel=17,
	outputFolder='data',xpixel=480,ypixel=360,epsg=None,elements=None):

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

	# Randomize elements list to make sure we don't download all pics from the
	# same sample

	element_list = []
	index_list = range(len(elements['features'])) #featue map
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements,epsg)
	shuffle(index_list)
	for i in index_list:
		element_list.append(elements['features'][i]) #feature map

	# Now we're gonna download the satellite images for these locations
	namespace= os.path.split(inputFile)[-1][:-5] #get input file name as namespace
	#create folders
	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	if not os.path.isdir(subpath):
		os.mkdir(subpath)
		print 'Directory',subpath,'created'
	if not os.path.isdir(subpath+satDataFolder):
		os.mkdir(subpath+satDataFolder)
		print 'Directory',subpath+satDataFolder,'created'

	mapbox_static = MapboxStatic(
	    namespace=namespace,
	    root_folder=subpath+satDataFolder[0:-1])

	total_downloaded = 0
	c = 0
	print "------------------- Getting Satellite data -------------------"
	for element in element_list:
		element_id_str = index_list[c]

			#sport = element.get('tags', {}).get('sport', 'unknown').lower()
			#if element_id_str in ways_data and sport == target_sport:
	#	print '> Element: %s (%s)' % (element.get('id'), sport)
	#	try: #feature map
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
					
#		except KeyError:  #OSM
#			latitude=element.get('lat')
#			longitude=element.get('lon')

		#get url
		print "Coordinates Native: "+str(av_lon)+','+str(av_lat)
		print "Coordinates WSG64: "+str(longitude)+','+str(latitude)
		url = mapbox_static.get_url(
			latitude=latitude,
			longitude=longitude,
			mapbox_zoom=zoomLevel,
			access_token=mapboxtoken,
			width=xpixel,
			height=ypixel)
		#print url
#		element_id_sport = '%s_%s' % (sport, element_id_str)
		#download data
		success = mapbox_static.download_tile(
		    element_id=index_list[c],
		    url=url,verbose=True)
		if success:
			total_downloaded += 1
			print total_downloaded,'/',count
		c += 1
		if total_downloaded >= count:
			break
