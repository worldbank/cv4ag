import sys,ok
from PIL import Image
from libs.foldernames import getPaths,imgsizefile
from modules.getFeatures import latLon,find_between,find_before
print 'Number of arguments:', len(sys.argv), 'arguments.'
print 'Argument List:', str(sys.argv)
cclass=int(sys.argv[1])
rootdir='kaggle/'

raster_lon=[0,304,304*2,304*3,304*4,304*5,304*6,304*7,304*8,304*9,304*10,304*11,304*12,304*13,304*14,304*15,304*16]
raster_lat=[0,224,224*2,224*3,224*4,224*5,224*6,224*7,224*8,224*9,224*10,224*11,224*12,224*13,224*14,224*15,224*16]
#ims = map(Image.open, 
#get all images
imgList=os.listdir(rootdir+'class'+str(cclass)+'/test')
#get csv
with open(imgsizefile,"rb") as csvfile:
	imgSizes= list(csv.reader(csvfile,delimiter=",",quotechar='"'))
for row in imgSizes:
	rootImage=row[0]
	W=row[1]
	H=row[2]
#get image array
	imgArr=[]
	for i in range(0,16):
		imgArr.append('o')
		for l in range(0,16):
			imgArr[i].append('o')
	for img in imgList:
		image_index=find_before(img,'___')
		if image_index==rootImage:
			av_lon=int(find_between(img,'___','_',True))
			av_lat=int(find_between(img,'_','.png',False))
			cnt=0
			for lon_raster in raster_lon:
				if av_lon==lon_raster:
					lon_cnt=cnt		
				cnt+=1
			cnt=0
			for lat_raster in raster_lat:
				if av_lat==lat_raster:
					lat_cnt=cnt		
				cnt+=1
			imgArr[lon_cnt][lat_cnt]=img
#concatenate
	print imgArr
	new_im = Image.new('L', (W, H))

x_offset = 0
for im in images:
  new_im.paste(im, (x_offset,0))
  x_offset += im.size[0]

new_im.save('test.jpg')
