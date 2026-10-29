'''
Boundary boxes of places, looked up with Nominatim (OpenStreetMap)
'''
import sys

import requests

NOMINATIM_ENDPOINT = 'https://nominatim.openstreetmap.org/search'
USER_AGENT = 'cv4ag (https://github.com/worldbank/cv4ag)'


def getBBox(area):
	'''area name and boundary box (west,south,east,north) of a place or "w s e n" string'''
	try:
		w,s,e,n=[float(v) for v in area.replace(","," ").split()]
		return "bbox_%g_%g_%g_%g" % (w,s,e,n),(w,s,e,n)
	except ValueError:
		pass
	if len(area)==2 and area.isalpha(): # ISO country code
		params={'country':area}
	else:
		params={'q':area}
	params.update({'format':'jsonv2','limit':1})
	response=requests.get(NOMINATIM_ENDPOINT,params=params,
		headers={'User-Agent':USER_AGENT},timeout=60)
	response.raise_for_status()
	results=response.json()
	if not results:
		print("Error: No place found for",area)
		sys.exit(1)
	print("Acquiring data for",results[0]['display_name'])
	s,n,w,e=[float(v) for v in results[0]['boundingbox']]
	return area,(w,s,e,n)
