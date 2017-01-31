#!usr/bin/python
"""
Top Layer for the Computer Vision 4 Agriculture (cv4ag) framework
Lukas Arnold
WB-DIME
Jan 30 2017

The framewoArk consists of four parts

1. Parsing input data
2. Downloading satellite images
3. Overlaying data with sattelite images
4. Training
5. Application
"""
import argparse,sys
import json
#import subdirectories to python path
sys.path.append('scripts')
sys.path.append('modules')
sys.path.append('lib')

def parse(inputFile=None,outputFolder=None,\
	scriptFile=None, scriptArg1=None,scriptArg2=None):
	"""
	Acquire and parse data
	
	'datatype': Data type (json or geoTiff)
	'outputFolder': Filename for output data
	'inputFile': Filename for input data
	'script': Script that returns input data. Has to contain script(.) function that returns a list with (datatiles,datatype)
	'scriptArg': Arguments for script, if any
	"""
	
	#Execute script, if given. This should allow to users to load data from 
	#custom scripts.
	if scriptFile:
		# import script file as module for input with and without .py ending
		if scriptFile[0:8] == "scripts/":
			scriptFile = scriptFile[8:] # delete folder if present
		if scriptFile[-3:] == ".py":
			scriptFile = scriptFile[0:-3] # delete .py ending if present
		scriptModule = __import__(scriptFile)
		
		#load according to how many arguments are given
		if scriptArg1:
			if scriptArg2:
				scriptReturn= scriptModule.script(scriptArg1,scriptArg2)
			else:
				scriptReturn= scriptModule.script(scriptArg1)
		else:
			scriptReturn= scriptModule.script()
		datatiles=	scriptReturn[0] #data
		datatype=	scriptReturn[1] #data type
	#or load data from inputfile
	else:
		pass

	#Parse to json, if elements are not json

	#Save	
	with open(outputFolder+"datatiles.json", 'w') as f:
	    json.dump(datatiles,f)
	print "Written to "+outputFolder+"datatiles.json"

def get_satellite():
	pass

def overlay():
	pass

def train():
	pass

def ml():
	pass

#Main
if __name__ == "__main__":
	# get options from command line
	class myParse(argparse.ArgumentParser): # override error message to show usage
		def error(self, message):
			sys.stderr.write('error: %s\n' % message)
			self.print_help()
			sys.exit(2)
	cmdParser = myParse(\
		description='Machine Learning Framework for Agricultural Data.',
		add_help=True)
	cmdParser.add_argument('MODULE',
		metavar='MODULE',
		type=str,default=False,
		help='The modules to be loaded. OPTIONS: \n\
			all - all modules.\n\
			parse - input file parser.\n\
			satellite - get satellite data.\n\
			overlay - overlay classification with satellite data. \n\
			train - train.\n\
			ml - apply machine learning algorithm.')
	cmdParser.add_argument('--i',
		type=str,default=None,
		help='Input file. Do not give if data obtained by script.')
	cmdParser.add_argument('--s',
		type=str,default=None,
		help='Script file to obtain data')
	cmdParser.add_argument('--o',
		type=str,default="data/",
		help='Output folder.')
	cmdParser.add_argument('--arg1',
		type=str,default=None,
		help='Argument 1 for script.')
	cmdParser.add_argument('--arg2',
		type=str,default=None,
		help='Argument 2 for script.')
	cmdArgs = vars(cmdParser.parse_args())
	selectedModule = cmdArgs.get('MODULE')
	inputFile = cmdArgs.get('i')
	outputFolder = cmdArgs.get('o')
	scriptFile = cmdArgs.get('s')
	scriptArg1 = cmdArgs.get('arg1')
	scriptArg2 = cmdArgs.get('arg2')
	
	# Execute according to options
	if selectedModule == 'all':
		parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2)
		get_satellite()
		overlay()
		train()
		ml()
	elif selectedModule == 'parse':
		parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2)
	elif selectedModule == 'satellite':
		get_satellite()
	elif selectedModule == 'overlay':
		overlay()
	elif selectedModule == 'train':
		train()
	elif selectedModule == 'mltrain':
		ml()
	else:
		print "error - no valid option"
		cmdParser.print_help()
