import numpy as np
import matplotlib.pyplot as plt
import os.path
import json
import scipy
import argparse
import math
import pylab
import sys
import caffe
from random import random
from sklearn.preprocessing import normalize
from libs.colorlist import colorlist
from PIL import Image
#caffe_root = '/home/worldbank-ml/ml/caffe-segnet/' 			# Change this to the absolute directoy to SegNet Caffe
#sys.path.insert(0, caffe_root + 'python')


def segment(model,weights,iterations,top,outpath,sat_imgs,compare=False):
	net = caffe.Net(os.path.abspath(model),
			os.path.abspath(weights),
			caffe.TEST)

	print "Iterations:",iterations
	for i in range(0, iterations):
		print "Image:",sat_imgs[i]
		net.forward()
		if random()>0.99:
			break
		image = net.blobs['data'].data
		if compare:
			label = net.blobs['label'].data
		predicted = net.blobs['prob'].data
		image = np.squeeze(image[0,:,:,:])
		output = np.squeeze(predicted[0,:,:,:])
		ind = np.argmax(output, axis=0)

		r = ind.copy()
		g = ind.copy()
		b = ind.copy()
		if compare:
			r_gt = label.copy()
			g_gt = label.copy()
			b_gt = label.copy()

		label_colors=[]
		for rgb in colorlist:
			label_colors.append([rgb[0],rgb[1],rgb[2]])
		label_colors=np.array(label_colors)
		for l in range(0,top):
			r[ind==l] = label_colors[l,0]
			g[ind==l] = label_colors[l,1]
			b[ind==l] = label_colors[l,2]
			if compare:
				r_gt[label==l] = label_colors[l,0]
				g_gt[label==l] = label_colors[l,1]
				b_gt[label==l] = label_colors[l,2]

		rgb = np.zeros((ind.shape[0], ind.shape[1], 3))
		rgb[:,:,0] = r/255.0
		rgb[:,:,1] = g/255.0
		rgb[:,:,2] = b/255.0
		if compare:
			rgb_gt = np.zeros((ind.shape[0], ind.shape[1], 3))
			rgb_gt[:,:,0] = r_gt/255.0
			rgb_gt[:,:,1] = g_gt/255.0
			rgb_gt[:,:,2] = b_gt/255.0

		image = image/255.0

		img = Image.open(sat_imgs[i])
		img = img.convert('L')
		img.putdata(rgb)
		img.save(outpath+os.path.split(sat_imgs[i])[-1])
		print 'Saved to',(outpath+os.path.split(sat_imgs[i])[-1])

		image = np.transpose(image, (1,2,0))
		output = np.transpose(output, (1,2,0))
		image = image[:,:,(2,1,0)]

		if random()>0.99 and 1==2:
			print "Show"
			#scipy.misc.toimage(rgb, cmin=0.0, cmax=255).\
			#	save(os.path.abspath(outpath+"testoutput"+'_i'+'_segnet.png')) #(name differently)
			plt.figure(i)
			plt.subplot(221)
			plt.imshow(image,vmin=0, vmax=1)
			if compare:
				plt.subplot(222)
				plt.imshow(rgb_gt,vmin=0, vmax=1)
			plt.subplot(223)
			plt.imshow(rgb,vmin=0, vmax=1)
			plt.show()
	print 'Success!'

