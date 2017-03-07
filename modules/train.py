import os
import caffe
import utils.computeStatistics
from libs.foldernames import *
from libs.models import *
from modules.getFeatures import find_before
from modules.get_stats import get_stats
from random import random
from shutil import copyfile

def train(outputFolder,inputFile,net=1,stats=None,key='Descriptio',\
	elements=None,top=15,ignorebackground=1,freq=None,createTest=False,xpixel=480,ypixel=360,
	mode="gpu",batchsize=None,maxiter=None,stepsize=None,datatype="PNG",initweights=True):
	#Get statistics if not in input
	if not stats:
		stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
			elements=elements)

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
	cnt=0
	cnt_test=0
	for f1 in os.listdir(satpath):
		try:
			id1= (find_before(f1,".png"))
			for f2 in os.listdir(trainpath):
				id2= (find_before(f2,"train.png"))
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
						#os.rename(satpath+f1,testpath+f1)
						copyfile(satpath+f1,testpath+f1)
						copyfile(trainpath+f2,verpath+f2)
						#os.rename(trainpath+f2,verpath+f2)
		except ValueError: #ignore metadata
			pass
	for f1 in os.listdir(testpath):
		try:
			id1= (find_before(f1,".png"))
			for f2 in os.listdir(verpath):
				id2= (find_before(f2,"train.png"))
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
		except ValueError: #ignore subfolder 
			pass

	print cnt,"files found for training. ",cnt_test,"files found for testing."

	#write solver
	print "Configure solver files and net..."
	solver_configured=solver.replace('PATH_TO_OUTPUT',str(os.path.abspath(weightpath)+"/"))
	solver_configured=solver_configured.replace\
		('PATH_TO_TRAINPROTOTXT',str(os.path.abspath(modelpath+trainprototxt)))
	if mode.lower()=='gpu':
		solver_configured=solver_configured.replace('OPTION_GPU_OR_CPU','GPU')
	elif mode.lower() =='cpu':
		solver_configured=solver_configured.replace('OPTION_GPU_OR_CPU','CPU')
	#net=2,3 extended training net, net=1 basic training net, net=0 very basic net
	if not stepsize:
		if net==0:
			stepsize=0.3
		elif net==1:
			stepsize=0.1
		elif net==2:
			stepsize=0.01
		elif net==3:
			stepsize=0.001
	solver_configured=solver_configured.replace('INSERT_BASE_LR',str(stepsize))
	if not maxiter:
		if net==0:
			maxiter=500
		elif net==1:
			maxiter=5000
		elif net==2:
			maxiter=20000
		elif net==3:
			maxiter=40000
	solver_configured=solver_configured.replace('INSERT_MAX_ITER',str(maxiter))

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
	net_configured=model
	inference_configured=inference

	if datatype.lower()=="png":	
		dtype='DenseImageData'
		netshuffle='shuffle: true'
		dataparam='dense_image_data_param'
		net_configured=net_configured.replace('DATALAYER',datalayer)
		inference_configured=inference_configured.replace('DATALAYER',datalayer)
	elif datatype.lower()[0:2]=="hdf":
		dtype='HDF5'
		netshuffle='shuffle: true'
		dataparam='hdf5_data_param'
		net_configured=net_configured.replace('DATALAYER',datalayer)
		inference_configured=inference_configured.replace('DATALAYER',datalayer)
	elif datatype.lower()=="lmdb":
		dtype='Data'
		netshuffle='backend: LMDB'
		dataparam='data_param'
		net_configured=net_configured.replace('DATALAYER',datalayer)
		inference_configured=inference_configured.replace('DATALAYER',datalayer)
	elif datatype.lower()=="lmdb2": #not completed. need different types and sources
		dtype='Data'
		netshuffle='backend: LMDB'
		dataparam='data_param'
		net_configured=net_configured.replace('DATALAYER',datalayer+datalayer)
		inference_configured=inference_configured.replace('DATALAYER',datalayer+datalayer)
	else:
		print "Error: Provide valid datatype (PNG, LMDB, LMDB2 or HDF5)."
		exit()
		
	net_configured=net_configured.replace('DATATYPE',dtype)
	inference_configured=inference_configured.replace('DATATYPE',dtype)
	net_configured=net_configured.replace('SHUFFLE',netshuffle)
	inference_configured=inference_configured.replace('SHUFFLE','')
	net_configured=net_configured.replace('DATAPARAM',dataparam)
	inference_configured=inference_configured.replace('DATAPARAM',dataparam)

	inference_configured=inference_configured.replace\
		('PATH_TO_SOURCE',str(os.path.abspath(indexpath+"test.txt"))) # to change
	net_configured=net_configured.replace('PATH_TO_SOURCE',str(os.path.abspath(indexpath+"train.txt")))
	if not batchsize:
		if net<3:
			batchsize=2
		else:
			batchsize=1
	net_configured=net_configured.replace('BATCHSIZE',str(batchsize))
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
	if net>1 or (xpixel == 480 and ypixel == 360):
		upsample_w_large= str(int(round(0.125*xpixel)))
		upsample_h_large= str(int(round(0.125*ypixel)))
		upsample_w_small=str(int(round(0.0625*xpixel)))
		upsample_h_small=str(int(round(0.0625*ypixel)))
	else:
		print "Error: Net < 2 only available for 480x360 pixel images. Chose other net or other size"
		exit()

	net_configured=net_configured.replace('UPSAMPLE_W_LARGE',upsample_w_large)
	net_configured=net_configured.replace('UPSAMPLE_H_LARGE',upsample_h_large)
	inference_configured=inference_configured.replace('UPSAMPLE_W_LARGE',upsample_w_large)
	inference_configured=inference_configured.replace('UPSAMPLE_H_LARGE',upsample_h_large)
	net_configured=net_configured.replace('UPSAMPLE_W_SMALL',upsample_w_small)
	net_configured=net_configured.replace('UPSAMPLE_H_SMALL',upsample_h_small)
	inference_configured=inference_configured.replace('UPSAMPLE_W_SMALL',upsample_w_small)
	inference_configured=inference_configured.replace('UPSAMPLE_H_SMALL',upsample_h_small)

	sumfreq=sum(freq)
	initweight=1./len(stats)
	classweights=''''''
	with open(subpath+"/meta_classlabels.txt",'w+') as f:
		f.write('')
			
	if not ignorebackground:
		if initweights:
			classweight=freq[0]*1./(8*sumfreq) #Background weight is set to same as first labelled class/8
		else:
			classweight=0.2
		print 'Weight for background:\t\t\t\t\t\t\t',classweight
		classweights+='class_weighting: '+str(classweight)+"\n"
		with open(subpath+"/meta_classlabels.txt",'a+') as f:
			f.write("0\tBackground")
				
	for i in range(0,len(stats)):
		#Create file with metadata
		if initweights:
			classweight=freq[i]*1./sumfreq #does not have to equal 1
		else:
			classweight=0.8
		classweights+='class_weighting: '+str(classweight)+"\n"
		numberoftabs=len(stats[i])/8	
		tabs="\t"*(6-numberoftabs)
		print 'Weight for class '+stats[i]+":"+tabs+str(classweight)
		with open(subpath+"/meta_classlabels.txt",'a+') as f:
			f.write(str(1+additionalclass)+"\t"+str(stats[i]))

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
	print weightpath+"_iter_"+str(maxiter)+".caffeemodel"
	if os.path.isfile(weightpath+"_iter_"+str(maxiter)+".caffemodel"):
		#overwrite=raw_input("_iter_"+str(maxiter)+".caffemodel exists. Overwrite? (y/n)")
		#if overwrite=="n":
		#else:
		#	caffesolver = caffe.get_solver(modelpath+solverprototxt)
		#	caffesolver.solve()
		#	del caffesolver
		if os.path.isfile(weightpath+weightsfile):
			print weightsfile,"already exists."
			pass
		else:
			utils.computeStatistics.compute(modelpath,trainprototxt,weightpath,weightsfile,xpixel,ypixel,maxiter)
	else:	
		caffesolver = caffe.get_solver(modelpath+solverprototxt)
		caffesolver.solve()
		del caffesolver
		utils.computeStatistics.compute(modelpath,trainprototxt,weightpath,weightsfile,xpixel,ypixel,maxiter)
	print "Training completed."
