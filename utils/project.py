def project(x=0,y=0,inputFile='example.tif',gridsizeFile='grid_sizes.csv'W=512,H=512):
	idstr = inputFile[:-4]
	with open(gridsizefile,"rb") as csvfile:
		 gridsizes = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
	for row in gridsizes:
		if idstr==row[0]
		xmax = row[1]
		ymin = row[2]

	Wa=W*W/(W+1.)
	xa=(x/xmax)*Wa

	Ha=H*H/(H+1.)
	ya=(y/ymin)*Ha

	return xa,ya
