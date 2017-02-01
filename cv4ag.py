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
import argparse,sys,os
sys.path.append('scripts')
sys.path.append('modules')
sys.path.append('lib')
import parse
#import subdirectories to python path
#-------------------------------------------------------------------

def get_satellite():
	pass

def overlay():
	pass

def train():
	pass

def ml():
	pass

#----------------------------------------------------------------------
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
		metavar='OPTION',
		type=str,default=False,
		help='The modules to be loaded. OPTION: \n\
			all - all modules.\n\
			parse - input file parser.\n\
			satellite - get satellite data.\n\
			overlay - overlay classification with satellite data. \n\
			train - train.\n\
			ml - apply machine learning algorithm.')
	cmdParser.add_argument('-i',
		type=str,default=None,metavar='FILE',
		help='Input file. Do not give if data obtained by script.')
	cmdParser.add_argument('-s',metavar='FILE',
		type=str,default=None,
		help='Script file to obtain data')
	cmdParser.add_argument('-o',metavar='PATH',
		type=str,default="data/",
		help='Output folder.')
	cmdParser.add_argument('-d',metavar='GDAL_CODE',
		type=str,default=None,
		help='Datatype. Will try to find automatically if not provided.\
			See www.gdal.org/formats_list.html and \
			www.gdal.org/ogr_formats.html, or libs/ogr_*_formats.csv for GDAL_CODEs.')
	cmdParser.add_argument('--arg1',
		type=str,default=None,
		help='Argument 1 for script.')
	cmdParser.add_argument('--arg2',
		type=str,default=None,
		help='Argument 2 for script.')
	cmdParser.add_argument('--arg3',
		type=str,default=None,
		help='Argument 3 for script.')
	cmdParser.add_argument('--arg4',
		type=str,default=None,
		help='Argument 4 for script.')
	cmdArgs = vars(cmdParser.parse_args())
	selectedModule = cmdArgs.get('MODULE')
	inputFile = cmdArgs.get('i')
	outputFolder = cmdArgs.get('o')
	datatype = cmdArgs.get('d')
	scriptFile = cmdArgs.get('s')
	scriptArg1 = cmdArgs.get('arg1')
	scriptArg2 = cmdArgs.get('arg2')
	scriptArg3 = cmdArgs.get('arg3')
	scriptArg4 = cmdArgs.get('arg4')
	
	# Execute according to options
	print "Option:",selectedModule
	if selectedModule == 'all':
		parse.parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,datatype=datatype,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2,
			scriptArg3=scriptArg3,scriptArg4=scriptArg4)
		get_satellite()
		overlay()
		train()
		ml()
	elif selectedModule == 'parse':
		parse.parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,datatype=datatype,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2,
			scriptArg3=scriptArg3,scriptArg4=scriptArg4)
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
