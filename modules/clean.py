#to test
import shutil

def clear(inputFile):
	if inputFile[-5:]==".json":
		rmDir=inputFile[-5:]+"/"
	else:
		rmDir=inputFile+"/"
	print 'Remove directory',inputFile
	shutil.rmtree(rmDir)
	print 'Done'

