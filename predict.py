from utils.gdal_polygonize_edited import polygonize
from utils.project import projectRev
from modules.getFeatures import latLon,find_between,find_before
from libs.foldernames import getPaths
import json,os,csv
submissionrows=[[],[],[],[],[],[],[],[],[],[]]

header='ImageId,ClassType,MultipolygonWKT'
for cl in range(0,1):
	print 'Class',cl+1
	outputFolder='kaggle/'
	inputFile='kaggle/class'+str(cl+1)+".json"
	subpath,satpath,trainpath,modelpath,weightpath,\
		indexpath,testpath,verpath,outpath=\
		getPaths(outputFolder,inputFile)	
	
	listImages=os.listdir(outpath)
	image_files = [f for f in listImages if f.endswith('.png')] 


	for imageInput in image_files:
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
		image_index=find_before(image,'___')
		av_lon=int(find_between(image,'___','_',True))
		av_lat=int(find_between(image,'_','train.png',False))
		l=0
		submissionrows[l]='''
'''+str(image_index)+","+str(cl+1)+","

		submissionrows[l]+="\"POLYGON ("
		for polygon in polygons:
			submissionrows[l]+="("
			init=False
			for coordinates in polygon:
				if init==True:
					submissionrows[l]+=','
				lon_init=coordinates[0]
				lat_init=coordinates[1]

				lotlan= projectRev(av_lon+lon_init,av_lat+lat_init,image_index,'.',3349,3391)
				longitude=lotlan[0]
				latitude=lotlan[1]
				submissionrows[l]+=str(longitude)+" "+str(latitude)
				init=True
			submissionrows[l]+=")"
		submissionrows[l]+=")\""

submission=header+submissionrows[l]
print submission
	#polygonize file

	#parse content into result file
