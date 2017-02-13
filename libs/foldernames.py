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
trainprototxt="segnet_train.prototxt"
inferenceprototxt="segnet_inference.prototxt"
solverprototxt="solver.prototxt"
weightsfile="weights.caffemodel"

def getPaths(outputFolder,inputFile):
	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
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
			os.mkdir(subpath+subsubpath)
			print 'Directory',subpath+subsubpath,'created'
	return subpath,satpath,trainpath,modelpath,weightpath,indexpath,testpath,verpath,outpath
