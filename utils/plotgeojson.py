from matplotlib import pyplot
from descartes import PolygonPatch
import math
import simplejson
 
 
def configurePlot():
    #set up the mapplotlib
    fig = pyplot.figure(1, figsize=(10, 4), dpi=180)
    ax = fig.add_subplot(121)
    return ax
 
def setPlotExtent(ax,data):
    #get feature extents (a property of the cloudmade geojson)
    #note this was previously bbox
    minx = data['bounds'][0][0]
    maxx = data['bounds'][1][0]
    miny = data['bounds'][0][1]
    maxy = data['bounds'][1][1]
 
    #set the graph axes to the feature extents
    ax.set_xlim(minx,maxx)
    ax.set_ylim(miny,maxy)
 
def plotFeature(coordlist, myplot):
    #create a polygon geojson-like feature
    poly = {"type": "Polygon", "coordinates": coordlist}
    patch = PolygonPatch(poly, fc='#6699cc', ec='#6699cc', alpha=0.5, zorder=2)
    #plot it on the graph
    myplot.add_patch(patch)
def plot(filename): 
#turn the geojson into a python object
	pydata = simplejson.loads(filename)
	print pydata
	 
	myplot = configurePlot()
	setPlotExtent(myplot,pydata)
	 
	#loop through each polygon in the MULTIPOLYGON collection
	for coordlist in pydata['features'][0]['geometry']['coordinates']:
	    plotFeature(coordlist, myplot)
	pyplot.show() 
	#save the plot as an image
	pyplot.savefig('myplot.png')
