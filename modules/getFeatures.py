import json
def getCoord(element):
	'''search geojson element for coordinates and return array of coordinates'''
	alat=[] #all lattitutes for nodes
	alon=[] #all longitudes for nodes
	try:
		for coordinate in element['geometry']['coordinates'][0][0]:
			alat.append(coordinate[1])
			alon.append(coordinate[0])
	except TypeError: # in case coordinates are located not that deep
		try:
			for coordinate in element['geometry']['coordinates'][0]:
				alat.append(coordinate[1])
				alon.append(coordinate[0])
		except TypeError: # in case coordinates are located not that deep
			try:
				for coordinate in element['geometry']['coordinates']:
					alat.append(coordinate[1])
					alon.append(coordinate[0])
			except TypeError:
				coordinate = element['geometry']['coordinates']
				alat.append(coordinate[1])
				alon.append(coordinate[0])
	return alon,alat

def latLon(element):
        '''
        get center of polygon of feature data
	return lattitude,longitude
        '''
	alon,alat=getCoord(element)
	#calculate center
	av_lat= (max(alat)+min(alat))/2 
	av_lon= (max(alon)+min(alon))/2
	return av_lon,av_lat

def getBBox(element):
        '''
	return minx,maxx,miny,maxy
        '''
	alon,alat=getCoord(element)
	return min(alon),max(alon),min(alat),max(alat)

def find_between(s, first, last=None, lastfirst=False ):
        '''find substrings. used to get index out of image filename'''
        try:
            start = s.rindex( first ) + len( first )
	    if last:
		if lastfirst:
			end = s.index(last,start)
		else:
			end = s.rindex( last, start )
            	return s[start:end]
	    else:
            	return s[start:]
        except ValueError:
            return "" 

def find_before(s, first):
        '''find substrings. used to get index out of image filename'''
	end = s.index(first)
	return s[:end]
