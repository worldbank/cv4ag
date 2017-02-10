import os
from libs.foldernames import *
from libs.models import *
from modules.getFeatures import find_between
from modules.get_stats import get_stats

def train(outputFolder,inputFile,net=0,stats=None,key='Descriptio',elements=None,top=15):
	#Get statistics if not in input
	if not stats:
		stats,_=get_stats(inputFile,top,verbose=True,key=key,\
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
	#create directories
	for subsubpath in [modelDataFolder,weightDataFolder,indexDataFolder]:
		if not os.path.isdir(subpath+subsubpath):
			os.mkdir(subpath+subsubpath)
			print 'Directory',subpath+subsubpath,'created'
	
	#Find matching indices and write to file
	filewritten=False
	for f1 in os.listdir(satpath):
		id1= int(find_between(f1,"_",".png"))
		for f2 in os.listdir(trainpath):
			id2= int(find_between(f2,"_","train.png"))
			if id1==id2:
				if filewritten==False: #create new file
					with open(indexpath+"/train.txt",'w+') as f:
						f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
							str(os.path.abspath(trainpath+"/"+f2)))
					filewritten=True
				else: #append file
					with open(indexpath+"/train.txt",'a+') as f:
						f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
							str(os.path.abspath(trainpath+"/"+f2)))

	#write solver
	print "Configure solver files and net..."
	solver_configured=solver.replace('PATH_TO_OUTPUT',str(os.path.abspath(weightpath)))
	solver_configured=solver.replace('PATH_TO_TRAINPROTOTXT',str(os.path.abspath(modelpath+"segnet_train.prototxt")))
	solver_configured=solver.replace('OPTION_GPU_OR_CPU','GPU')
	if net==0:
		solver_configured=solver.replace('INSERT_BASE_LR',str(0.3))
	elif net==1:
		solver_configured=solver.replace('INSERT_BASE_LR',str(0.1))
	elif net==2:
		solver_configured=solver.replace('INSERT_BASE_LR',str(0.001))

	if net==0:
		solver_configured=solver.replace('INSERT_MAX_ITER',str(500))
	elif net==1:
		solver_configured=solver.replace('INSERT_BASE_LR',str(10000))
	elif net==2:
		solver_configured=solver.replace('INSERT_BASE_LR',str(40000))

	with open(modelpath+"segnet_solver.prototxt","w+") as f:
		f.write(solver_configured)

	#write net
	if net==0:
		model=nets[0]
	elif net==1:
		model=nets[1]
	elif net==2:
		model=nets[2]
	solver_configured=solver.replace('PATH_TO_TRAINPROTOTXT',str(os.path.abspath(indexpath+"train.txt")))
	solver_configured=solver.replace('INSERT_IGNORE_LABEL','')
	
	solver_configured=solver.replace('INSERT_IGNORE_LABEL','')
