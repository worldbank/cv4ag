#!usr/bin/python
'''
Get satellite data according to input file.
'''
from random import shuffle
from utils.mapbox_static import MapboxStatic
from utils.coordinate_converter import CoordConvert
import os,json
def get_satellite(inputFile=None,mapboxtoken=None,count=1000,zoomLevel=17,outputFolder='data'):
	if not inputFile:
		print "Error: Provide input file."
		exit()
	if not mapboxtoken:
		print "Error: Provide mapbox token (visit www.mapbox.com)."
		exit()
	#parser.add_argument('--sport',
	 #   type=str, default='baseball',
	  #  help='Sport tag, for example: baseball, tennis, or soccer.')

	# We need the elements
	print 'Loading %s...' % inputFile
	with open(inputFile, 'r') as f:
		elements = json.load(f)

	# Randomize elements list to make sure we don't download all pics from the
	# same sample

	# Given list1 and list2
	element_list = []
	try:
		index_list = range(len(elements['features'])) #featue map
		myCoordConvert = CoordConvert()
		code=myCoordConvert.getCoordSystem(elements)
	except TypeError:
		index_list = range(len(elements)) #OSM map
	shuffle(index_list)
	for i in index_list:
		try:
			element_list.append(elements['features'][i]) #feature map
		except TypeError:
			element_list.append(elements[i]) #OSM map

	# Now we're gonna download the satellite images for these locations
	_,namespace= os.path.split(inputFile) #get input file name as namespace
	mapbox_static = MapboxStatic(
	    namespace=namespace,
	    root_folder=outputFolder+'/sat')

	total_downloaded = 0
	c = 0
	for element in element_list:
		element_id_str = index_list[c]

		#sport = element.get('tags', {}).get('sport', 'unknown').lower()
		#if element_id_str in ways_data and sport == target_sport:
		if total_downloaded >= count:
			break
	#	print '> Element: %s (%s)' % (element.get('id'), sport)
		try: #feature map
			#figure out center of polygon
			alat=[] #all lattitutes for nodes
			alon=[] #all longitudes for nodes
			for coordinate in element['geometry']['coordinates'][0][0]:
				alat.append(coordinate[0])
				alon.append(coordinate[1])
			#calculate center
			av_lat=	(max(alat)+min(alat))/2 
			av_lon= (max(alon)+min(alon))/2
			#Convert to standard format
			if code != 4319: # if not already in wgs84 standard format
				latlon= myCoordConvert.convert(av_lat,av_lon)
				latitude=latlon[1]
				longitude=latlon[0]
			else: #if already in wgs84 format
				latitude= av_lat
				longitude= av_lot
					
		except KeyError:  #OSM
			latitude=element.get('lat')
			longitude=element.get('lon')

		#get url
		print "Coordinates: "+str(latitude)+','+str(longitude)
		url = mapbox_static.get_url(
			latitude=latitude,
			longitude=longitude,
			mapbox_zoom=17,
			access_token=mapboxtoken)
#		print url
#		element_id_sport = '%s_%s' % (sport, element_id_str)
		#download data
		success = mapbox_static.download_tile(
		    element_id=index_list[c],
		    url=url,verbose=True)
		if success:
			total_downloaded += 1
			print total_downloaded+1,'/',count
		c += 1
