'''
Apply the trained model to the test images and compare with the labels
'''
import os,sys
import numpy as np
from PIL import Image
from libs.colorlist import colorlist
from libs.foldernames import *
from modules.segmentation import *

def colorize(label):
	'''class ids to RGB colors, background black'''
	palette=np.zeros((256,3),dtype=np.uint8)
	for i,color in enumerate(colorlist[:255]):
		palette[i+1]=color[:3]
	return palette[label]

def apply(outputFolder,inputFile,mode='gpu',ignorebackground=None,top=15,epsg=None,compare=True):
	'''
	Classify the images in test/. Writes the class id per pixel to out/<image>
	and image | prediction | label to out/<image>_vis.png. If compare is set,
	per-class IoU, precision and recall are written to out/metrics.json.
	'''
	outputFolder=stripSatFolder(outputFolder)
	subpath,satpath,trainpath,modelpath,weightpath,\
		indexpath,testpath,verpath,outpath=\
		getPaths(outputFolder,inputFile)

	if not os.path.isfile(weightpath+weightsfile):
		print("Error: No trained model found in",weightpath,"- run train first.")
		sys.exit(1)
	device=pick_device(mode)
	model,checkpoint=load_checkpoint(weightpath+weightsfile,device)
	classes=checkpoint['classes']
	#a model trained without background cannot predict it
	ignorebackground=checkpoint['ignorebackground']
	print("Model:",checkpoint['encoder'],"trained for",checkpoint['iteration'],"iterations")

	if compare and os.path.isfile(indexpath+"test.txt"):
		pairs=read_pairs(indexpath+"test.txt")
	else:
		compare=False
		pairs=[(os.path.abspath(testpath+f),None) for f in sorted(os.listdir(testpath))\
			if f.endswith('.png')]
	if not pairs:
		print("Error: No test images in",testpath)
		sys.exit(1)

	cm=np.zeros((len(classes),len(classes)),dtype=np.int64)
	for i,(image_path,label_path) in enumerate(pairs):
		name=os.path.split(image_path)[-1]
		image=load_image(image_path)
		pred=predict(model,image,device,ignorebackground)
		Image.fromarray(pred,mode='L').save(outpath+name)
		panels=[image,colorize(pred)]
		if compare:
			label=load_label(label_path,ignorebackground)
			cm+=confusion_matrix(pred,label,len(classes))
			panels.append(colorize(np.where(label==IGNORE_INDEX,0,label)))
		Image.fromarray(np.concatenate(panels,1)).save(outpath+name[:-4]+"_vis.png")
		print(str(i+1)+'/'+str(len(pairs)),'Saved to',outpath+name)

	if compare:
		result=scores(cm,classes)
		print('')
		print(format_scores(result))
		write_scores(outpath+metricsfile,result)
		print("Metrics written to",outpath+metricsfile)
	print('Success!')
