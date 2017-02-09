#!usr/bin/python
'''
Print some stats on all the elements we've found
'''

import json
import operator

def get_stats(filename,top=15,key='Descriptio',verbose=True,elements=None):
	'''
	Shows statistics of features. 

	'filename': filename
	'top': show statistics for the first top categories
	'key': Look for this keyword within feature map
	'''
	# Load the file
	print 'Loading %s...' % filename
	elements = []
	counter = 0
	if not elements:
		with open(filename, 'r') as f:
			elements = json.load(f)
	print 'Total elements found: %d' % len(elements['features']) #GeoJSON conversion
	# Stats
	stats = {}
	elements_stats = {}
	#For feature maps
	for feature in elements['features']:
		try:
			type_key = feature['properties'][key]
		except KeyError:
			print "Error: Keyword",key,"not found in",filename
			print "Cannot get statistics..."
			exit()
			return 0
			
		stats[type_key] = (stats[type_key]+1)\
			if type_key in stats else 1
		#print feature['geometry']['coordinates']

	#print "Total elements",elements_stats

	# Sort the type_keys by value, and reverse (descending values)
	stats = sorted(stats.items(), key=operator.itemgetter(1))
	stats = list(reversed(stats))
	if verbose:
		print "Frequency statistics of",top,"most common properties:"
	# Show statistics
	listofmostelements = []
	for type_key_stat in stats[:top]:
		numberoftabs=len(type_key_stat[0])/8	
		tabs="\t"*(6-numberoftabs)
		listofmostelements.append(type_key_stat[0])
		if verbose:
			print type_key_stat[0]+tabs+str(type_key_stat[1])
	return listofmostelements,elements
