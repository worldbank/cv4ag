#!usr/bin/python
"""
Script to download Open Street Map data of land use
Lukas Arnold
WB-DIME
Jan 31 2017
"""
from country_bounding_boxes import (
      country_subunits_containing_point,
      country_subunits_by_iso_code
    )

def script(countryISO='US'):
	"""
	Main function executed by top

	'countryISO': Country for which BBox data should be downloaded
	"""
	subunits=[]
	#Load country data
	for c in country_subunits_by_iso_code(countryISO):
		subunits.append(c)
	#Chose subunits, if more than 1
	subunit=1
	if len(subunits)>1:
		cnt = 1
		print 	"Subunits:"
		for c in subunits:
			print cnt,"- ",c.name			
			cnt += 1
		subunit=input('Chose subunit: ')
	#Get BBox data
	print "Acquiring data for",subunits[subunit-1].name
