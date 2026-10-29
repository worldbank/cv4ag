'''
Train a U-Net on the satellite images (sat/) and class label images (train/)
'''
import os,math,random,sys,time
from collections import Counter
from shutil import copyfile
import numpy as np
import torch
import segmentation_models_pytorch as smp
from PIL import Image
from libs.foldernames import *
from modules.get_stats import get_stats
from modules.overlay import readFootprints
from modules.segmentation import *

#net=0..3: default number of iterations
DEFAULT_MAXITER={0:2000,1:5000,2:10000,3:20000}

def findPairs(imagepath,labelpath):
	'''images <name>.png with a label image <name>train.png, by image name'''
	if not os.path.isdir(imagepath) or not os.path.isdir(labelpath):
		return {}
	labels=set(os.listdir(labelpath))
	return {f:(os.path.abspath(imagepath+f),os.path.abspath(labelpath+f[:-4]+"train.png"))\
		for f in sorted(os.listdir(imagepath))\
		if f.endswith('.png') and f[:-4]+"train.png" in labels}

def spatialSplit(names,footprints,fraction=0.2,blocksize=5,seed=0):
	'''
	Split tiles into training and test tiles by spatial blocks of
	blocksize x blocksize tiles, so that the test set is not made of
	neighbours of training tiles. Training tiles that overlap a test tile are
	dropped. Tiles without footprint are assigned randomly.

	Returns training names, test names, dropped names
	'''
	rng=random.Random(seed)
	located=[n for n in names if n in footprints]
	test=set(n for n in names if n not in footprints and rng.random()<fraction)
	dropped=set()
	if located:
		bounds=np.array([footprints[n][1] for n in located])
		tilesize=np.median(np.maximum(bounds[:,2]-bounds[:,0],bounds[:,3]-bounds[:,1]))
		centers=np.stack([(bounds[:,0]+bounds[:,2])/2,(bounds[:,1]+bounds[:,3])/2],1)
		#use smaller blocks if the data cover only a few blocks
		while True:
			cells=[tuple(c) for c in np.floor(centers/(blocksize*tilesize)).astype(int)]
			cellcount=Counter(cells)
			if len(cellcount)>=10 or blocksize<=1:
				break
			blocksize/=2.
		order=sorted(cellcount)
		rng.shuffle(order)
		chosen=set()
		ntest=0
		for cell in order:
			if ntest>=fraction*len(located):
				break
			chosen.add(cell)
			ntest+=cellcount[cell]
		testmask=np.array([c in chosen for c in cells])
		test.update(n for n,t in zip(located,testmask) if t)
		testbounds=bounds[testmask]
		for n,b,t in zip(located,bounds,testmask):
			if not t and np.any((testbounds[:,0]<b[2])&(testbounds[:,2]>b[0])&\
				(testbounds[:,1]<b[3])&(testbounds[:,3]>b[1])):
				dropped.add(n)
	train=[n for n in names if n not in test and n not in dropped]
	return train,sorted(test),sorted(dropped)

def classWeights(pairs,num_classes,ignorebackground=False,maxweight=10.):
	'''
	median frequency balancing on pixel counts: rare classes get weights > 1,
	frequent classes < 1. Returns weights and pixel counts per class.
	'''
	counts=np.zeros(num_classes)
	for _,label in pairs:
		counts+=np.bincount(np.asarray(Image.open(label).convert('L')).ravel(),
			minlength=256)[:num_classes]
	if ignorebackground:
		counts[0]=0
	weights=np.ones(num_classes)
	present=counts>0
	freq=counts[present]/counts.sum()
	weights[present]=np.clip(np.median(freq)/freq,1./maxweight,maxweight)
	return weights,counts

def seedWorker(worker_id):
	np.random.seed(torch.initial_seed()%2**32)

def train(outputFolder,inputFile,net=1,stats=None,key='Descriptio',\
	elements=None,top=15,ignorebackground=False,freq=None,createTest=False,xpixel=480,ypixel=360,
	mode="gpu",batchsize=None,maxiter=None,stepsize=None,initweights=True,
	encoder=None,pretrained=True,seed=0,testfraction=0.2):
	#Get statistics if not in input
	if not stats:
		stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
			elements=elements)

	outputFolder=stripSatFolder(outputFolder)

	##########################################
	# Create Folders
	subpath,satpath,trainpath,modelpath,weightpath,indexpath,testpath,verpath,_=\
		getPaths(outputFolder,inputFile)

	##########################################
	# Training and test set
	pairs=findPairs(satpath,trainpath)
	if createTest:
		footprints=readFootprints(trainpath+footprintsfile)
		trainnames,testnames,dropped=spatialSplit(sorted(pairs),footprints,
			fraction=testfraction,seed=seed)
		#replace test set of a previous run (copies of files in sat/ and train/)
		for f in os.listdir(testpath):
			if f in pairs:
				os.remove(testpath+f)
		for f in os.listdir(verpath):
			if f.endswith("train.png") and f[:-9]+".png" in pairs:
				os.remove(verpath+f)
		for name in testnames:
			copyfile(pairs[name][0],testpath+name)
			copyfile(pairs[name][1],verpath+name[:-4]+"train.png")
		print(len(testnames),"tiles copied to test set,",len(dropped),\
			"tiles next to test tiles left out.")
	else: #tiles in the test folder are never used for training
		trainnames=[n for n in pairs if not os.path.isfile(testpath+n)]
	trainpairs=[pairs[n] for n in trainnames]
	testpairs=list(findPairs(testpath,verpath).values())
	write_pairs(indexpath+"train.txt",trainpairs)
	write_pairs(indexpath+"test.txt",testpairs)
	print(len(trainpairs),"files found for training. ",len(testpairs),"files found for testing.")
	if not trainpairs:
		print("Error: No training images. Run overlay first.")
		sys.exit(1)

	classes=['Background']+[str(s) for s in stats]
	with open(subpath+"/meta_classlabels.txt",'w') as f:
		f.write("\n".join(str(i)+"\t"+name for i,name in enumerate(classes))+"\n")

	##########################################
	# Class weights
	weights,counts=classWeights(trainpairs,len(classes),ignorebackground)
	if not initweights:
		weights=np.ones(len(classes))
	print("%-40s %8s %8s" % ("class","pixels","weight"))
	for name,count,weight in zip(classes,counts,weights):
		if ignorebackground and name=='Background':
			continue
		print("%-40s %7.2f%% %8.3f" % (name[:40],100.*count/max(counts.sum(),1),weight))
		if count==0:
			print("\tWarning: no pixels of class",name,"in training images")

	##########################################
	# Model and training settings
	encoder=encoder or ENCODERS[net]
	maxiter=maxiter or DEFAULT_MAXITER[net]
	batchsize=batchsize or 8
	stepsize=stepsize or 5e-4
	device=pick_device(mode)
	random.seed(seed)
	np.random.seed(seed)
	torch.manual_seed(seed)
	crop=crop_size(trainpairs)
	print("Encoder:",encoder,"(ImageNet pretrained)" if pretrained else "")
	print("Device:",device,"Batch size:",batchsize,"Crop:",crop,\
		"Learning rate:",stepsize,"Iterations:",maxiter)

	workers=min(4,os.cpu_count() or 1)
	loader=torch.utils.data.DataLoader(
		TileDataset(trainpairs,crop=crop,augment=True,ignorebackground=ignorebackground),
		batch_size=batchsize,shuffle=True,drop_last=len(trainpairs)>=batchsize,
		num_workers=workers,persistent_workers=True,worker_init_fn=seedWorker,
		pin_memory=device.type=='cuda')
	model=build_model(encoder,len(classes),pretrained).to(device)
	celoss=torch.nn.CrossEntropyLoss(
		weight=torch.tensor(weights,dtype=torch.float32,device=device),
		ignore_index=IGNORE_INDEX)
	diceloss=smp.losses.DiceLoss('multiclass',ignore_index=IGNORE_INDEX)
	optimizer=torch.optim.AdamW(model.parameters(),lr=stepsize,weight_decay=1e-4)
	scheduler=torch.optim.lr_scheduler.OneCycleLR(optimizer,max_lr=stepsize,
		total_steps=maxiter,pct_start=0.05)

	def save(path,iteration,result=None):
		torch.save({'state_dict':model.state_dict(),'encoder':encoder,'classes':classes,
			'ignorebackground':ignorebackground,'iteration':iteration,'scores':result},path)

	##########################################
	# Start training
	evalinterval=max(maxiter//10,1)
	best=-1.
	iteration=0
	losses=[]
	start=time.time()
	log=open(weightpath+"train_log.csv","w")
	log.write("iteration,loss,learning_rate,test_miou\n")
	while iteration<maxiter:
		stepped=False
		for x,y in loader:
			if not (y!=IGNORE_INDEX).any(): #nothing to learn
				continue
			stepped=True
			model.train()
			x,y=x.to(device),y.to(device)
			with torch.autocast(device.type,dtype=torch.bfloat16,enabled=device.type=='cuda'):
				logits=model(x)
			logits=logits.float()
			loss=celoss(logits,y)+diceloss(logits,y)
			optimizer.zero_grad(set_to_none=True)
			loss.backward()
			optimizer.step()
			scheduler.step()
			iteration+=1
			losses.append(loss.item())
			miou=''
			if iteration%evalinterval==0 or iteration==maxiter:
				if testpairs:
					result=evaluate(model,testpairs,classes,device,ignorebackground)
					miou='%.4f' % result['miou']
					print("Iteration",iteration,"test mean IoU:",miou)
					if result['miou']>best:
						best=result['miou']
						save(weightpath+weightsfile,iteration,result)
				save(weightpath+lastweightsfile,iteration)
			if iteration%20==0 or iteration==maxiter:
				print("Iteration %d/%d loss %.4f lr %.2e (%.0fs)" % (iteration,maxiter,\
					np.mean(losses[-20:]),scheduler.get_last_lr()[0],time.time()-start))
			log.write("%d,%.5f,%.3e,%s\n" % (iteration,losses[-1],scheduler.get_last_lr()[0],miou))
			if iteration>=maxiter:
				break
		if not stepped:
			print("Error: Training images contain no labelled pixels.")
			sys.exit(1)
	log.close()
	if not testpairs:
		copyfile(weightpath+lastweightsfile,weightpath+weightsfile)
	else:
		print("Best test mean IoU: %.4f" % best)
	print("Model written to",weightpath+weightsfile)
	print("Training completed.")
