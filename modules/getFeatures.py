import json

def latLon(element):
        '''
        get center of polygon of feature data
	return lattitude,longitude
        '''
	alat=[] #all lattitutes for nodes
	alon=[] #all longitudes for nodes
	for coordinate in element['geometry']['coordinates'][0][0]:
		alat.append(coordinate[0])
		alon.append(coordinate[1])
	#calculate center
	av_lat= (max(alat)+min(alat))/2 
	av_lon= (max(alon)+min(alon))/2
	return av_lat,av_lon
	
