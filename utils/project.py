import csv

def project(x=0,y=0,idstr='0',inputFolder='.',W=512,H=512):
	'''Transform from GIS coordinate to pixel'''
	gridsizefile=inputFolder+"/"+'grid_sizes.csv'
	with open(gridsizefile,"rb") as csvfile:
		 gridsizes = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
	for row in gridsizes:
		if idstr==row[0]:
			xmax = float(row[1])
			ymin = float(row[2])
	Wa=W*W/(W+1.)
	xa=(x/xmax)*Wa

	Ha=H*H/(H+1.)
	ya=(y/ymin)*Ha
	return xa,ya

def projectRev(x=0,y=0,idstr='0',inputFolder='.',W=512,H=512):
	'''Transform from pixel to GIS coordinate'''
	gridsizefile=inputFolder+"/"+'grid_sizes.csv'
	with open(gridsizefile,"rb") as csvfile:
		 gridsizes = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
	for row in gridsizes:
		if idstr==row[0]:
			xmax = float(row[1])
			ymin = float(row[2])
	Wa=W*W/(W+1.)
	xa=(x*xmax)/Wa

	Ha=H*H/(H+1.)
	ya=(y*ymin)/Ha
	return xa,ya
