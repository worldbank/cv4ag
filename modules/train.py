import os
from libs.foldernames import *
from modules.getFeatures import find_between

def train(outputFolder,inputFile):
	#set outputFolder to directory above the /sat directory
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]==satDataFolder[1:-1]:
		outputFolder=outputFolder[0:-4]

	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	satpath=subpath+satDataFolder
	trainpath=subpath+trainingDataFolder
	
	#Find matching indices and write to file
	with open(subpath+"/train.txt",'w+') as f:
		f.write('')
	for f1 in os.listdir(satpath):
		id1= int(find_between(f1,"_",".png"))
		for f2 in os.listdir(trainpath):
			id2= int(find_between(f2,"_","train.png"))
			if id1==id2:
				with open(subpath+"/train.txt",'a+') as f:
					f.write("\n"+str(os.path.abspath(satpath+"/"+f1))+" "+\
						str(os.path.abspath(trainpath+"/"+f2)))
