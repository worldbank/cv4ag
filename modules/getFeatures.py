import json

def latLon(element):
        '''
        get center of polygon of feature data
	return lattitude,longitude
        '''
	alat=[] #all lattitutes for nodes
	alon=[] #all longitudes for nodes
	for coordinate in element['geometry']['coordinates'][0][0]:
		alat.append(coordinate[1])
		alon.append(coordinate[0])
	#calculate center
	av_lat= (max(alat)+min(alat))/2 
	av_lon= (max(alon)+min(alon))/2
	return av_lon,av_lat

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

