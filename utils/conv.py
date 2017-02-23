from osgeo import gdal
from PIL import Image
def transform(value)
	'''Transform coordinates (for values above 256)'''
	return int(round((value-100.)/4.))
#Open existing dataset 
def tif2png(inputFile,outputFile):
	'''Convert GeoTIFF to 8-bit RGB PNG'''
	src_ds = gdal.Open( inputFile ) 

	#Open output format driver, see gdal_translate --formats for list 
	format = "PNG"
	driver = gdal.GetDriverByName( format )

	ds = gdal.Open(inputFile)
	band1= ds.GetRasterBand(1)
	band2= ds.GetRasterBand(2)
	band3= ds.GetRasterBand(3)
	r = band1.ReadAsArray()
	g = band2.ReadAsArray()
	b = band3.ReadAsArray()
	#plt.figure(1)
	#plt.imshow(r)
	#plt.figure(2)
	#plt.imshow(g)
	#plt.figure(3)
	#plt.imshow(r)
	#plt.show()
	#Output to new format
	dst_ds = driver.CreateCopy( outputFile, src_ds, 1 )
	img = Image.open(outputFile)
	datas = img.getdata()
	newData = []
	y=0
	x=0
	for item in datas:
		rgb=(transform(r[x][y]),transform(g[x][y]),transform(b[x][y]))
		newData.append(rgb)
		if y<len(r[0])-1:
			y+=1
		else:
			print str(x)+"\r",
			y=0
			x+=1
	img.putdata(newData)
	img.save(outputFile)
