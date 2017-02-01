'''
Print some stats on all the elements we've found
'''

import json
import operator

def get_stats(filename):
	# Load the file
	print 'Loading %s...' % filename
	elements = []
	counter = 0
	with open(filename, 'r') as f:
		elements = json.load(f)
	print 'Total elements found: %d' % len(elements)

	# Stats
	stats = {}
	elements_stats = {}
	for element in elements:
	    element_type = element.get('type')

	    # Find the most popular 
	    if element_type == 'way':
		sport = element.get('tags', {}).get('landuse', 'unknown').lower()
		stats[sport] = (stats[sport] + 1) \
		    if sport in stats else 1

	    # Build type stats (nodes and ways)
	    elements_stats[element_type] = (elements_stats[element_type] + 1) \
		if element_type in elements_stats else 1

	print elements_stats

	# Sort the sports by value, and reverse (descending values)
	stats = sorted(stats.items(), key=operator.itemgetter(1))
	stats = list(reversed(stats))

	for sport_stat in stats[:10]:
	    print sport_stat
