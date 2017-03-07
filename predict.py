from utils.gdal_polygonize_edited import polygonize
from utils.project import projectRev
from modules.getFeatures import latLon,find_between,find_before
from libs.foldernames import getPaths,imgsizefile
import json,os,csv
submissionrows=[[],[],[],[],[],[],[],[],[],[]]
poly={}
outputFolder='kaggle/'
header='ImageId,ClassType,MultipolygonWKT'
classlist=range(0,10)
for cl in classlist:
	print 'Class',cl+1
	inputFile=outputFolder+'class'+str(cl+1)+".json"
	subpath,satpath,trainpath,modelpath,weightpath,\
		indexpath,testpath,verpath,outpath=\
		getPaths(outputFolder,inputFile)	
	
	listImages=os.listdir(outpath)
	image_files = [f for f in listImages if f.endswith('.png')] 

	icnt=0
	for imageInput in image_files:
		icnt+=1
		print icnt
		print imageInput
		inputFile=outpath+os.path.split(imageInput)[-1]
		outputFile='polygonized.json'
		os.remove(outputFile)
		polygonize(inputFile,outputFile,'GeoJSON')
		with open(outputFile, 'r') as f:
			elements = json.load(f)

		polygons=[]
		cnt=0
		for element in elements['features']:
			if element['properties']['DN']==1:
				for polygon1 in element['geometry']['coordinates']:
					polygons.append([])
					for coordinates in polygon1:
						polygons[cnt].append(coordinates)
					cnt+=1

		image=os.path.split(inputFile)[-1]
		#image_index=find_before(image,'___')
		#av_lon=int(find_between(image,'___','_',True))
		#av_lat=int(find_between(image,'_','.png',False))
		image_index=find_before(image,'.png')
		av_lon=0
		av_lat=0

		if image_index in poly.keys():
			pass
		else:
			poly[image_index]=[[],[],[],[],[],[],[],[],[],[]]
		l=0

		with open(imgsizefile,"rb") as csvfile:
			 imgSizes= list(csv.reader(csvfile,delimiter=",",quotechar='"'))
		for imgSize in imgSizes:
			if imgSize[0]==image_index:
				W=int(imgSize[1])
				H=int(imgSize[2])
				break

		for polygon in polygons:
			polygonstr="(("
			init=False
			for coordinates in polygon:
				if init==True:
					polygonstr+=','
				lon_init=coordinates[0]
				lat_init=coordinates[1]

				lotlan= projectRev(av_lon+lon_init,av_lat+lat_init,image_index,'.',W,H)
				longitude=lotlan[0]
				latitude=lotlan[1]
				polygonstr+=str(longitude)+" "+str(latitude)
				init=True
			polygonstr+="))"
			poly[image_index][cl].append(polygonstr)

submission=''+header
for key in poly.keys():
	for cl in classlist:
		submission+='''
'''+str(key)+","+str(cl+1)+","
		if not poly[key][cl]:
			submission+='MULTIPOLYGON EMPTY'
		else:
			submission+="\"MULTIPOLYGON ("
			init=False
			for pol in poly[key][cl]:
				if init==True:
					submission+=','
				submission+=pol
				init=True
			submission+=")\""
print submission

with open('submission.csv', 'w+') as f:
	f.write(submission)
	#polygonize file

	#parse content into result file
