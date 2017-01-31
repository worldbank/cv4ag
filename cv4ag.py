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

def parse(inputFile=None,outputFile=None,\
	scriptFile=None, scriptArg=None):
	"""
	Acquire and parse data
	
	'datatype': Data type (json or geoTiff)
	'outputFile': Filename for output data
	'inputFile': Filename for input data
	'script': Script that returns input data. Has to contain script(.) function
	'scriptArg': Arguments for script, if any
	"""
	
	#Execute script, if given
	if scriptFile:
		# import script file as module for input with and without .py ending
		if scriptFile[0:8] == "scripts/":
			scriptFile = scriptFile[8:] # delete folder if present
		if scriptFile[-3:] == ".py":
			scriptFile = scriptFile[0:-3] # delete .py ending if present
		scriptModule = __import__(scriptFile)

		if scriptArg:
			data = scriptModule.script(scriptArg)
		else:
			data = scriptModule.script()

	#Parse to json

	#Save	
	pass

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
		type=str,default=None,
		help='Output file.')
	cmdParser.add_argument('--scriptarg',
		type=str,default=None,
		help='Argument for script.')
	cmdArgs = vars(cmdParser.parse_args())
	selectedModule = cmdArgs.get('MODULE')
	inputFile = cmdArgs.get('i')
	outputFile = cmdArgs.get('o')
	scriptFile = cmdArgs.get('s')
	scriptArg = cmdArgs.get('scriptarg')
	
	# Execute according to options
	if selectedModule == 'all':
		parse(inputFile=inputFile,outputFile=outputFile,
			scriptFile=scriptFile,scriptArg=scriptArg)
		get_satellite()
		overlay()
		train()
		ml()
	elif selectedModule == 'parse':
		parse(inputFile=inputFile,outputFile=outputFile,
			scriptFile=scriptFile,scriptArg=scriptArg)
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
