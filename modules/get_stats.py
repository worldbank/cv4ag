'''
Print some stats on all the elements we've found
'''

import json
import operator
import os.path
import sys

def get_stats(filename,top=15,key='Descriptio',verbose=True,elements=None):
	'''
	Shows statistics of features.

	'filename': filename
	'top': show statistics for the first top categories
	'key': Look for this keyword within feature map
	'elements': GeoJSON data, if already loaded
	'''
	print('\tGet statistics...')
	if not elements:
		print("\tFile size ~",int(os.path.getsize(filename)/1000000),"MB")
		print('\tLoading %s...' % filename)
		with open(filename, 'r') as f:
			elements = json.load(f)
	print('\tTotal elements found: %d' % len(elements['features'])) #GeoJSON conversion
	# Stats
	stats = {}
	#For feature maps
	for feature in elements['features']:
		try:
			type_key = str(feature['properties'][key])
		except KeyError:
			print("Error: Keyword",key,"not found in",filename)
			print("Cannot get statistics...")
			sys.exit(1)

		stats[type_key] = stats.get(type_key,0)+1

	# Sort the type_keys by value, and reverse (descending values)
	stats = sorted(stats.items(), key=operator.itemgetter(1), reverse=True)
	if verbose:
		print("\tFrequency statistics of",top,"most common properties:")
	# Show statistics
	listofmostelements = []
	numberofmostelements = []
	for type_key_stat in stats[:top]:
		listofmostelements.append(type_key_stat[0])
		numberofmostelements.append(type_key_stat[1])
		if verbose:
			print("\t%-48s%d" % (type_key_stat[0],type_key_stat[1]))
	return listofmostelements,numberofmostelements,elements
