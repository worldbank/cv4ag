import os
import caffe
import csv
from libs.foldernames import *
from utils.segment import segment
from modules.get_stats import get_stats

def apply(outputFolder,inputFile,mode='gpu',ignorebackground=True,top=15,epsg=None,compare=False):#,stats=None,key='Descriptio'):
	#set outputFolder to directory above the /sat directory
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]==satDataFolder[1:-1]:
		outputFolder=outputFolder[0:-4]
	#Get statistics if not in input
	#if not stats:
	#	elements=None
	#	stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
	#		elements=elements)

	subpath,satpath,trainpath,modelpath,weightpath,\
		indexpath,testpath,verpath,outpath=\
		getPaths(outputFolder,inputFile)	
	#if epsg!=9999:
	#	image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png') \
	#		and f.startswith(os.path.split(inputFile)[-1][:-5])]
	#else:
	#	image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png')]
	if compare:
		with open(indexpath+"test.txt","rb") as csvfile:
			 image_files = list(csv.reader(csvfile,delimiter=" ",quotechar='"'))
	else:
		imgindx=indexpath+"test.txt"
		image_files = [f for f in os.listdir(testpath) if f.endswith('.png')]
		init=False
		for image in image_files:
			if init==False:
				with open(imgindx,"w+") as f:
					f.write(os.path.abspath(testpath+image))
				init=True
			else:
				with open(imgindx,"a+") as f:
					f.write('''
'''+os.path.abspath(testpath+image))


			
		
	sat_imgs=[]
	train_imgs=[]
	if compare:
		for row in image_files:
			sat_imgs.append(os.path.abspath(testpath+row[0]))
			train_imgs.append(os.path.abspath(verpath+row[1]))
	else:
		for row in image_files:
			sat_imgs.append(os.path.abspath(testpath+row))
	if mode.lower()=='gpu':
		caffe.set_device(0)
		caffe.set_mode_gpu()
	elif mode.lower() =='cpu':
		caffe.set_mode_cpu()
	else:
		print "Error: indicate mode (cpu or gpu)"
		exit()
	if ignorebackground:
		nbClasses=len(stats)
	else:
		nbClasses=top+1
	segment(modelpath+inferenceprototxt,weightpath+weightsfile,len(image_files),nbClasses,outpath,sat_imgs,compare)
