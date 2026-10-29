import os.path

satDataFolder="/sat/"
trainingDataFolder="/train/"
checkDataFolder="/check/"
testDataFolder="/test/"
verificationDataFolder=testDataFolder+"ver/"
featureDataFolder="/feature/"
modelDataFolder="/models/"
weightDataFolder="/weights/"
indexDataFolder="/imgindex/"
outDataFolder="/out/"
weightsfile="model.pt"
lastweightsfile="last.pt"
imgsizefile="imgsizes.csv"
tilesfile="tiles.csv"			# in sat/: center and zoom of downloaded tiles
footprintsfile="footprints.csv"	# in train/: georeferenced bounds of each label image
metricsfile="metrics.json"

def dataName(inputFile):
	'''name of the data set, derived from the input file name'''
	return os.path.splitext(os.path.split(inputFile)[-1])[0]

def getPaths(outputFolder,inputFile):
	subpath=outputFolder+"/"+dataName(inputFile)
	satpath=subpath+satDataFolder
	trainpath=subpath+trainingDataFolder
	modelpath=subpath+modelDataFolder
	weightpath=subpath+weightDataFolder
	indexpath=subpath+indexDataFolder
	testpath=subpath+testDataFolder
	verpath=subpath+verificationDataFolder
	outpath=subpath+outDataFolder
	#create directories
	for subsubpath in [modelDataFolder,weightDataFolder,indexDataFolder,\
		testDataFolder,verificationDataFolder,outDataFolder]:
		if not os.path.isdir(subpath+subsubpath):
			os.makedirs(subpath+subsubpath)
			print('Directory',subpath+subsubpath,'created')
	return subpath,satpath,trainpath,modelpath,weightpath,indexpath,testpath,verpath,outpath

def stripSatFolder(outputFolder):
	'''set outputFolder to directory above the /sat directory'''
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]==satDataFolder[1:-1]:
		outputFolder=outputFolder[0:-4]
	return outputFolder
