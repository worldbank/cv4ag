from osgeo import gdal
from libs.foldernames import satDataFolder

def get_satfromfile(inputFile,count=1000,
	outputFolder='data',xpixel=480,ypixel=360,epsg=None,elements=None,
	randomImages=False):

	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	if not os.path.isdir(subpath):
		os.mkdir(subpath)
		print 'Directory',subpath,'created'
	if not os.path.isdir(subpath+satDataFolder):
		os.mkdir(subpath+satDataFolder)
		print 'Directory',subpath+satDataFolder,'created'

	#Open existing dataset
	src_ds = gdal.Open( inputFile )

	#Open output format driver, see gdal_translate --formats for list
	format = "PNG"
	driver = gdal.GetDriverByName( format )

	#Output to new format
	dst_ds = driver.CreateCopy( satDataFolder+inputFile[:-5]+".png", src_ds, 0 )

	#Cut file, with coordinates
