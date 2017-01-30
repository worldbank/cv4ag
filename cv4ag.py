'''
Top Layer for the Computer Vision 4 Agriculture (cv4ag) framework
Lukas Arnold
WB-DIME
Jan 30 2017

The framewoArk consists of four parts

1. Parsing of input data
2. Downloading satellite images
3. Overlaying data with sattelite images
4. Training
5. Application
'''
import parser

def parsing('datatype',inputData=None,script=None):
	"""
	Acquire and parse data
	
	'datatype': Data type (json or geoTiff)
	'inputData': Filename for input data
	'script': Script that returns input data
	"""
	if script:
		data = script()	
				
	#Execute script

	#Parse to json

	#Save	
	pass

def get_satellite():
	pass

def overlay():
	pass

def train():
	pass

def ml():
	pass
