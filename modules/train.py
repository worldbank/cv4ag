import os
import caffe
import utils.computeStatistics
from libs.foldernames import *
from libs.models import *
from modules.getFeatures import find_between
from modules.get_stats import get_stats
from random import random

def train(outputFolder,inputFile,net=1,stats=None,key='Descriptio',\
	elements=None,top=15,ignorebackground=1,freq=None,createTest=False,xpixel=480,ypixel=360,
	mode="gpu"):
	#Get statistics if not in input
	if not stats:
		stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
			elements=elements)

	#net=2 extended training net, net=1 basic training net, net=0 very basic net
	#set outputFolder to directory above the /sat directory
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]==satDataFolder[1:-1]:
		outputFolder=outputFolder[0:-4]

	##########################################
	# Create Folders
	subpath,satpath,trainpath,modelpath,weightpath,indexpath,testpath,verpath,_=\
		getPaths(outputFolder,inputFile)	
	# Get model files
	
	filewritten=False
	filewrittenTest=False

	#Find matching indices and write to file
	try:
		cnt=0
		cnt_test=0
		for f1 in os.listdir(satpath):
			id1= int(find_between(f1,"_",".png"))
			for f2 in os.listdir(trainpath):
				id2= int(find_between(f2,"_","train.png"))
				if id1==id2:
				#Put ~20% of images into test folder if createTest set
					randomValue=random()
					if randomValue>=0.2 or not createTest:
						cnt+=1
						if filewritten==False: #create new file
							with open(indexpath+"/train.txt",'w+') as f:
								f.write(str(os.path.abspath(satpath+"/"+f1))+" "+\
									str(os.path.abspath(trainpath+"/"+f2)))
							filewritten=True
						else: #append file
							with open(indexpath+"/train.txt",'a+') as f:
								f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
									str(os.path.abspath(trainpath+"/"+f2)))
					else:
						print "Move",f1,"and",f2
						os.rename(satpath+f1,testpath+f1)
						os.rename(trainpath+f2,verpath+f2)
		for f1 in os.listdir(testpath):
			try:
				id1= int(find_between(f1,"_",".png"))
				for f2 in os.listdir(verpath):
					id2= int(find_between(f2,"_","train.png"))
					if id1==id2:
						cnt_test+=1
						if filewrittenTest==False: #create new file
							with open(indexpath+"/test.txt",'w+') as f:
								f.write(str(os.path.abspath(testpath+"/"+f1))+" "+\
									str(os.path.abspath(verpath+"/"+f2)))
							filewrittenTest=True
						else: #append file
							with open(indexpath+"/test.txt",'a+') as f:
								f.write("\n"+str(os.path.abspath(testpath+"/"+f1))+" "+\
									str(os.path.abspath(verpath+"/"+f2)))
			except ValueError: #ignore subfolders
				pass
	except ValueError: #ignore metafile
		pass
	print cnt,"files found for training",cnt_test,"files found for testing."

	#write solver
	print "Configure solver files and net..."
	solver_configured=solver.replace('PATH_TO_OUTPUT',str(os.path.abspath(weightpath)+"/"))
	solver_configured=solver_configured.replace\
		('PATH_TO_TRAINPROTOTXT',str(os.path.abspath(modelpath+trainprototxt)))
	if mode.lower()=='gpu':
		solver_configured=solver_configured.replace('OPTION_GPU_OR_CPU','GPU')
	elif mode.lower() =='cpu':
		solver_configured=solver_configured.replace('OPTION_GPU_OR_CPU','CPU')
	if net==0:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.3))
	elif net==1:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.1))
	elif net==2:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.1))
	elif net==3:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.001))

	if net==0:
		solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(500))
	elif net==1:
		solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(10000))
	elif net==2:
		solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(20000))
	elif net==3:
		solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(40000))

	with open(modelpath+solverprototxt,"w+") as f:
		f.write(solver_configured)

	#write net
	if net==0:
		model=nets[0]
		inference=inferences[0]
	elif net==1:
		model=nets[0]
		inference=inferences[0]
	elif net==2:
		model=nets[1]
		inference=inferences[1]
	elif net==3:
		model=nets[1]
		inference=inferences[1]
	inference_configured=inference.replace\
		('PATH_TO_TESTTXT',str(os.path.abspath(indexpath+"test.txt"))) # to change

	net_configured=model.replace('PATH_TO_TRAINTXT',str(os.path.abspath(indexpath+"train.txt")))
	if net<3:
		net_configured=net_configured.replace('BATCHSIZE',str(2))
		inference_configured=inference_configured.replace('BATCHSIZE',str(2))
	else:
		net_configured=net_configured.replace('BATCHSIZE',str(1))
		inference_configured=inference_configured.replace('BATCHSIZE',str(1))
	if ignorebackground:
		ignorelabel='ignore_label: 0'
		firstclass = 1
		additionalclass = 0
	else:
		ignorelabel=''
		firstclass = 0
		additionalclass = 1
	net_configured=net_configured.replace('INSERT_IGNORE_LABEL',ignorelabel)

	sumfreq=sum(freq)
	initweight=1./len(stats)
	classweights=''''''
	with open(subpath+"/meta_classlabels.txt",'w+') as f:
		f.write('')
			
	if not ignorebackground:
		classweight=freq[0]*1./(4*sumfreq) #Background weight is set to same as first labelled class/4
		print 'Weight for background:\t\t\t\t\t\t\t',classweight
		classweights+='class_weighting: '+str(classweight)+"\n"
		with open(subpath+"/meta_classlabels.txt",'a+') as f:
			f.write("0\tBackground")
				
	for i in range(0,len(stats)):
		#Create file with metadata
		classweight=freq[i]*1./sumfreq #does not have to equal 1
		classweights+='class_weighting: '+str(classweight)+"\n"
		numberoftabs=len(stats[i])/8	
		tabs="\t"*(6-numberoftabs)
		print 'Weight for class '+stats[i]+":"+tabs+str(classweight)
		with open(subpath+"/meta_classlabels.txt",'a+') as f:
			f.write(str(1+additionalclass)+"\tBackground")

	net_configured=net_configured.replace\
		('INSERT_NUM_CLASSES',str(len(stats)+additionalclass)) #number of classes
	inference_configured=inference_configured.replace\
		('INSERT_NUM_CLASSES',str(len(stats)+additionalclass)) #number of classes
	net_configured=net_configured.replace('INSERT_CLASS_WEIGHTING',str(classweights))
	with open(modelpath+trainprototxt,"w+") as f:
		f.write(net_configured)
	with open(modelpath+inferenceprototxt,"w+") as f:
		f.write(inference_configured)
	print "Model files written to",modelpath
	##########################################
	# Start training

	if mode.lower()=='gpu':
		print "GPU mode"
		caffe.set_device(0)
		caffe.set_mode_gpu()
	elif mode.lower() =='cpu':
		print "CPU mode"
		caffe.set_mode_cpu()
	else:
		print "Error: indicate mode (cpu or gpu)"
		exit()
	caffesolver = caffe.get_solver(modelpath+solverprototxt)
	a=caffesolver.solve()
	print a
	utils.computeStatistics.compute(modelpath,trainprototxt,weightpath,weightsfile,xpixel,ypixel)
	print "Training completed."
