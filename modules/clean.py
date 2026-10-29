import shutil
from libs.foldernames import dataName,stripSatFolder

def clear(inputFile,outputFolder="data"):
	'''remove everything generated for inputFile in outputFolder'''
	rmDir=stripSatFolder(outputFolder)+"/"+dataName(inputFile)+"/"
	print('Remove directory',rmDir)
	shutil.rmtree(rmDir)
	print('Done')
