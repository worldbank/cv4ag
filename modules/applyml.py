import os
import caffe
from libs.foldernames import *
from utils.segment import segment
from modules.get_stats import get_stats

def apply(outputFolder,inputFile,mode='gpu',ignorebackground=True,top=15,epsg=None):#,stats=None,key='Descriptio'):
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
	if epsg!=9999:
		image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png') \
			and f.startswith(os.path.split(inputFile)[-1][:-5])]
	else:
		image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png')]
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
	segment(modelpath+inferenceprototxt,weightpath+weightsfile,len(image_files),nbClasses,outpath)
