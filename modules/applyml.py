import os
import caffe
from libs.foldernames import *
from utils.segment import segment

def apply(outputFolder,inputFile,mode='gpu',top=15,ignorebackground=True):
	subpath,satpath,trainpath,modelpath,weightpath,\
		indexpath,testpath,verpath,outpath=\
		getPaths(outputFolder,inputFile)	
	image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png') \
		and f.startswith(os.path.split(inputFile)[-1][:-5])] 
	if mode.lower()=='gpu':
		caffe.set_device(0)
		caffe.set_mode_gpu()
	elif mode.lower() =='cpu':
		caffe.set_mode_cpu()
	else:
		print "Error: indicate mode (cpu or gpu)"
		exit()
	if ignorebackground:
		nbClasses=top
	else:
		nbClasses=top+1
	segment(modelpath+inferenceprototxt,weightpath+weightsfile,len(image_files),nbClasses)
