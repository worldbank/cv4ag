#!usr/bin/python
'''
Print some stats on all the elements we've found
'''

import json
import operator

def get_stats(filename,topnr=15):
	# Load the file
	print 'Loading %s...' % filename
	elements = []
	counter = 0
	print filename
	with open(filename, 'r') as f:
		elements = json.load(f)
	try: 
		print 'Total elements found: %d' % len(elements['features']) #GeoJSON conversion
	except TypeError:
		print 'Total elements found: %d' % len(elements) #OSM
	# Stats
	stats = {}
	elements_stats = {}
	#For feature maps
	try:
		for feature in elements['features']:
			type_key = feature['properties']['Descriptio']
			stats[type_key] = (stats[type_key]+1)\
				if type_key in stats else 1
			#print feature['geometry']['coordinates']
	except TypeError:
		#For OSM data 
		for element in elements:
			try:
				element_type = element.get('type')
				# Find the most popular 
				if element_type == 'way':
					type_key = element.get('tags', {}).get('landuse', 'unknown').lower()
					stats[type_key] = (stats[type_key] + 1) \
						if type_key in stats else 1

				# Build type stats (nodes and ways)
				elements_stats[element_type] = (elements_stats[element_type] + 1) \
					if element_type in elements_stats else 1
			except AttributeError:
				pass

	print "Total elements",elements_stats

	# Sort the type_keys by value, and reverse (descending values)
	stats = sorted(stats.items(), key=operator.itemgetter(1))
	stats = list(reversed(stats))
	print "Frequency statistics of",topnr,"most common proporties:"
	# Show statistics
	for type_key_stat in stats[:topnr]:
		numberoftabs=len(type_key_stat[0])/8	
		tabs="\t"*(6-numberoftabs)
		print type_key_stat[0]+tabs+str(type_key_stat[1])
