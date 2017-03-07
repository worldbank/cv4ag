import sys,os,csv
from PIL import Image
from libs.foldernames import getPaths,imgsizefile
from modules.getFeatures import latLon,find_between,find_before
from multiprocessing import Pool
#print 'Number of arguments:', len(sys.argv), 'arguments.'
#print 'Argument List:', str(sys.argv)
#cclass=int(sys.argv[1])
outfolder='/home/ubuntu/data/concat/'
cropfolder='/home/ubuntu/data/concat/crop/'
traindir='/home/ubuntu/data/geojson/'

raster_lon=[0,304,304*2,304*3,304*4,304*5,304*6,304*7,304*8,304*9,304*10,304*11,304*12,304*13,304*14,304*15,304*16]
raster_lat=[0,224,224*2,224*3,224*4,224*5,224*6,224*7,224*8,224*9,224*10,224*11,224*12,224*13,224*14,224*15,224*16]
#ims = map(Image.open, 
#get all images
imgList=os.listdir(outfolder)#+'class'+str(cclass)+'/test')
#get csv
with open(imgsizefile,"rb") as csvfile:
	imgSizes= list(csv.reader(csvfile,delimiter=",",quotechar='"'))
#cnt=0
minx=10000
miny=10000
for row in imgSizes:
	if int(row[1])<minx:
		minx=int(row[1])
	if int(row[2])<miny:
		miny=int(row[2])
print minx,miny
def conc(row):
	rootImage=row[0]
	print rootImage
	convert=True
	for trainingImage in os.listdir(traindir):	
		if trainingImage==rootImage:
			convert=False
			print rootImage,'is training data.'
	if os.path.isfile(outfolder+rootImage+'.png'):
		convert=False
		if not os.path.isfile(cropfolder+rootImage+'.png'):
			print rootImage,'exists. Crop...'
			try:
				img=Image.open(outfolder+rootImage+'.png')
				img = img.crop((0, 0, minx, miny))
			except IOError:
				img = Image.new('RGB', (minx, miny))
			img.save(cropfolder+rootImage+'.png')
#	if convert==True:
		#cnt+=1
		#print cnt,'/',len(imgSizes)
#		W=int(row[1])
#		H=int(row[2])
#		new_im = Image.new('RGB', (W, H))
#		for img in imgList:
#			image_index=find_before(img,'___')
#			if image_index==rootImage:
#				av_lon=int(find_between(img,'___','_',True))
#				av_lat=int(find_between(img,'_','.png',False))
#				try:
#					im=Image.open(rootdir+img)
#					new_im.paste(im, (av_lon,av_lat))
#				except IOError:
#					print 'Could not identify',img
#		new_im.save(outfolder+rootImage+'.png')


pool = Pool()
pool.map(conc, imgSizes)
pool.close()
pool.join()
print minx,miny
#get image array
	#imgArr=[]
	#for i in range(0,16):
	#	imgArr.append([])
	#	for l in range(0,16):
	#		imgArr[i].append('o')
	#		cnt=0
	#		for lon_raster in raster_lon:
	#			if av_lon==lon_raster:
	#				lon_cnt=cnt		
	#			cnt+=1
	#		cnt=0
	#		for lat_raster in raster_lat:
	#			if av_lat==lat_raster:
	#				lat_cnt=cnt		
	#			cnt+=1
	#		imgArr[lat_cnt][lon_cnt]=img
	#for i in range(0,len(imgArr)):
	#	imgArr[i]=filter(lambda a: a != 'o', imgArr[i])
	#imgArr=filter(lambda a: a != [], imgArr)
#concatenate
	#print imgArr
	#for imgRow in imgArr:

