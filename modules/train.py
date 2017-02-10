import os
from libs.foldernames import *
from libs.models import *
from modules.getFeatures import find_between
from modules.get_stats import get_stats
from random import random

def train(outputFolder,inputFile,net=0,stats=None,key='Descriptio',elements=None,top=15,ignorebackground=1,freq=None,createTest=False):
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

	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	satpath=subpath+satDataFolder
	trainpath=subpath+trainingDataFolder
	modelpath=subpath+modelDataFolder
	weightpath=subpath+weightDataFolder
	indexpath=subpath+indexDataFolder
	testpath=subpath+indexDataFolder
	verpath=subpath+verificationDataFolder
	#create directories
	for subsubpath in [modelDataFolder,weightDataFolder,indexDataFolder,\
		testDataFolder,verificationDataFolder]:
		if not os.path.isdir(subpath+subsubpath):
			os.mkdir(subpath+subsubpath)
			print 'Directory',subpath+subsubpath,'created'
	
	filewritten=False
	filewrittenTest=False
	


	#Find matching indices and write to file
	for f1 in os.listdir(satpath):
		id1= int(find_between(f1,"_",".png"))
		for f2 in os.listdir(trainpath):
			id2= int(find_between(f2,"_","train.png"))
			if id1==id2:
			#Put ~20% of images into test folder if createTest set
				randomValue=random()
				print randomValue
				if randomValue>=0.2 or not createTest:
					if filewritten==False: #create new file
						with open(indexpath+"/train.txt",'w+') as f:
							f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
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
					if filewrittenTest==False: #create new file
						with open(indexpath+"/test.txt",'w+') as f:
							f.write("\n"+str(os.path.abspath(testpath+"/"+f1))+" "+\
								str(os.path.abspath(verpath+"/"+f2)))
						filewrittenTest=True
					else: #append file
						with open(indexpath+"/test.txt",'a+') as f:
							f.write("\n"+str(os.path.abspath(testpath+"/"+f1))+" "+\
								str(os.path.abspath(verpath+"/"+f2)))

	#write solver
	print "Configure solver files and net..."
	solver_configured=solver.replace('PATH_TO_OUTPUT',str(os.path.abspath(weightpath)))
	solver_configured=solver_configured.replace('PATH_TO_TRAINPROTOTXT',str(os.path.abspath(modelpath+"segnet_train.prototxt")))
	solver_configured=solver_configured.replace('OPTION_GPU_OR_CPU','GPU')
	if net==0:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.3))
	elif net==1:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.1))
	elif net==2:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(0.001))

	if net==0:
		solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(500))
	elif net==1:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(10000))
	elif net==2:
		solver_configured=solver_configured.replace('INSERT_BASE_LR',str(40000))

	with open(modelpath+"segnet_solver.prototxt","w+") as f:
		f.write(solver_configured)

	#write net
	if net==0:
		model=nets[0]
		inference=inferences[0]
	elif net==1:
		model=nets[1]
		inference=inferences[1]
	elif net==2:
		model=nets[1]
		inference=inferences[1]
	inference_configured=inference.replace('PATH_TO_TESTTXT',str(os.path.abspath(indexpath+"test.txt"))) # to change

	net_configured=model.replace('PATH_TO_TRAINTXT',str(os.path.abspath(indexpath+"train.txt")))
	net_configured=net_configured.replace('BATCHSIZE',str(2))
	if ignorebackground:
		ignorelabel='ignore_label: 0'
		firstclass = 1
		additionalclass = 0
	else:
		ignorelabel=''
		firstclass = 0
		additionalclass = 1
	net_configured=net_configured.replace('INSERT_IGNORE_LABEL',ignorelabel)

	filewritten=False
	sumfreq=sum(freq)
	initweight=1./len(stats)
	classweights=''''''
	cnt=0 #count number of labelled classes
	for i in range(firstclass,len(stats)):
		#Create file with metadata
		if filewritten==False: #create new file
			with open(subpath+"/meta_classlabels.txt",'w+') as f:
				f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
					str(os.path.abspath(trainpath+"/"+f2)))
			filewritten=True
		else: #append file
			with open(subpath+"/meta_classlabels.txt",'a+') as f:
				f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
					str(os.path.abspath(trainpath+"/"+f2)))
		classweight=freq[cnt]*1./sumfreq #does not have to equal 1
		classweights+='class_weighting: '+str(classweight)+"\n"
		if i==0: #i=0 is background. Background weight is set to same as first labelled class
			print 'Weight for background:\t\t\t\t\t\t',classweight
		else:
			numberoftabs=len(stats[cnt])/8	
			tabs="\t"*(6-numberoftabs)
			print 'Weight for class '+stats[cnt]+":"+tabs+str(classweight)
			cnt+=1
	net_configured=net_configured.replace('INSERT_NUM_CLASSES',str(len(stats)-firstclass)) #number of classes
	inference_configured=inference_configured.replace('INSERT_NUM_CLASSES',str(len(stats)+additionalclass)) #number of classes
	net_configured=net_configured.replace('INSERT_CLASS_WEIGHTING',str(classweights))
	with open(modelpath+"segnet_train.prototxt","w+") as f:
		f.write(net_configured)
	with open(modelpath+"segnet_inference.prototxt","w+") as f:
		f.write(inference_configured)
	print "Model files written to",modelpath
