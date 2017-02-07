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
from utils.overpass_client import OverpassClient
import json

# Query string to OSM to provide landuse data, with the query key later
# placed in the middle
query_begin = '''\
way
  ['''
query_end=''']
  ({query_bb_s},{query_bb_w},{query_bb_n},{query_bb_e});
(._;>;);
out;
'''
# Output is OSM format

datatype="OSM"

def script(countryISO='US',query='landuse',outputFolder='data/',
	outputFile='OSMdatatiles.json'):
	"""
	Main function executed by top

	'countryISO': Country for which BBox data should be downloaded
	Returns list with [filename,datatype], where datatype is the
		GDAL_CODE
	"""
	subunits=[]
	#Load country data
	for c in country_subunits_by_iso_code(countryISO):
		subunits.append(c)
	#Chose subunits, if more than 1
	subunit=1
	if len(subunits)>1: #if there are subunits
		cnt = 1
		print 	"Subunits:"
		for c in subunits:
			print cnt,"- ",c.name			
			cnt += 1
		subunit=input('Chose subunit: ')
	elif len(subunits)==0: #if nothing found
		print "Error: No country or entry with ISO code",countryISO
		exit()
	#Get BBox data for country
	print "Acquiring data for",subunits[subunit-1].name
	bbox = subunits[subunit-1].bbox #0-w, 1-s, 2-e, 3-n
	w = bbox[0]
	s = bbox[1]
	e = bbox[2]
	n = bbox[3]
	print "Coordinates:",w,s,e,n

	print "Key:",query

	# Country is split into 100 boxes, as (for the us) sample is too big
	# (timeout)
	# Number of Boxes = (samples-1)^2 boxes.
	samples = 11  # 100 boxes
	fullquery = query_begin+query+query_end
	#Get Elements from OSM
	overpass_client = OverpassClient(endpoint='fr')
	d = overpass_client.get_bbox_elements(
	    ql_template=fullquery,
	    bb_s=s, bb_w=w, bb_n=n, bb_e=e,
	    samples=samples)
	print 'Total elements found: %d' % len(d)
	
	# Save the result
	fileName=outputFolder+'/'+outputFile
	geojson= '''
		{
	    "type": "FeatureCollection",
		"crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::4326" } },
	    "features": ['''
	cnt = 0.
	lene=len(d)
	for e in d :
		print cnt*100./lene,"% done.\r", 
		cnt+=1
		if e['type']=='way':
	#		if  e['area']=='yes':
				geojson+='''
				    {
					"type": "Feature",'''+\
						"\n\t\t\t\"properties\":{\"Descriptio\":\""+\
						e['tags']['landuse']+"\"},"
				geojson+='''
					"geometry" : {
					    "type": "MultiPolygon",
					    "coordinates":[[['''
				for node in e['nodes']:
					for e2 in d: 
						if (e2['type']=='node' and e2['id'] == node):
							geojson+="["+str(e2['lon'])+","+str(e2['lat'])+"],"
							break
				geojson=geojson[0:-1]+"]]]}},"
	geojson=geojson[0:-1]+"\n]\n}"
	with open(fileName, 'w+') as f:
			json.dump(geojson,f)
	#replace escape characters
	with open(fileName, 'r') as file :
	  filedata = file.read()[1:-1]

	# Replace the target string
	filedata = filedata.replace('\\n', '')
	filedata = filedata.replace('\\t', '')
	filedata = filedata.replace('\\"', '"')

	# Write the file out again
	with open(fileName, 'w') as file:
	  file.write(filedata)

	print "Written to",fileName
	return [fileName,datatype]
