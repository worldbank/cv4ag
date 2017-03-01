from osgeo import gdal
from PIL import Image
import os
maindir='../geojson/'

def transform(value):
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

def crop(inputFile,inputSizeX,inputSizeY,outputFolder='.'):
	'''Crops images into subimages of size 'inputSize'x'inputSize'''
	x=0
	y=0
	img = Image.open(inputFile)
	width, height = img.size
	print width,height
	while not ((x+inputSizeX>width) or (y+inputSizeY>height)):
		img_small = img.crop((x,y,x+inputSizeX,y+inputSizeY))
		saveFile=outputFolder+'/'+os.path.split(inputFile)[-1][:-4]+"___"+str(x)+'_'+str(y)+".png"
		img_small.save(saveFile)
		if x+2*inputSizeX>width:
			x=0
			y=y+inputSizeY
		else:
			x = x + inputSizeX

if __name__ == "__main__":
	for trainingData in os.listdir(maindir):	
		for fileName in os.listdir('.'):
			if trainingData==fileName[:-4]:
				if fileName[-4:]==".tif":
					print 'convert', fileName
					fullsize=maindir+fileName[:-4]+'/'+fileName[:-4]+'.png'
					print 'full size image:',fullsize
					tif2png(fileName,fullsize)
					satPath=os.path.abspath(maindir+os.path.split(fileName)[-1][:-4]+'/sat/')
					print satPath
					crop(fullsize,303,223,satPath)
		#		os.mkdir(fileName[-4:]
