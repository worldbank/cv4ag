'''
Semantic segmentation model, data loading and evaluation shared by
train.py and applyml.py.

Label images contain the class id per pixel: 0 is background, 1..N are the
N most frequent classes of the GIS file.
'''
import json
import numpy as np
import torch
import torch.nn.functional as F
import segmentation_models_pytorch as smp
from PIL import Image

IGNORE_INDEX = 255
# -n option: size of the (ImageNet pretrained) encoder of the U-Net
ENCODERS = {0:'resnet18',1:'resnet34',2:'resnet50',3:'resnext50_32x4d'}
MEAN = np.array([0.485,0.456,0.406],dtype=np.float32)*255
STD = np.array([0.229,0.224,0.225],dtype=np.float32)*255

def pick_device(mode='gpu'):
	if mode.lower()=='cpu':
		return torch.device('cpu')
	if torch.cuda.is_available():
		return torch.device('cuda')
	if torch.backends.mps.is_available():
		return torch.device('mps')
	print("Warning: No GPU found. Using CPU.")
	return torch.device('cpu')

def build_model(encoder,num_classes,pretrained=True):
	return smp.Unet(encoder_name=encoder,
		encoder_weights='imagenet' if pretrained else None,
		classes=num_classes)

def load_checkpoint(path,device):
	checkpoint=torch.load(path,map_location=device,weights_only=False)
	model=build_model(checkpoint['encoder'],len(checkpoint['classes']),pretrained=False)
	model.load_state_dict(checkpoint['state_dict'])
	return model.to(device).eval(),checkpoint

def read_pairs(indexfile):
	'''image/label pairs of an index file (imgindex/train.txt or test.txt)'''
	pairs=[]
	with open(indexfile) as f:
		for line in f:
			if line.strip():
				pairs.append(tuple(line.split()))
	return pairs

def write_pairs(indexfile,pairs):
	with open(indexfile,'w') as f:
		f.write("\n".join(" ".join(pair) for pair in pairs))

def load_image(path):
	return np.asarray(Image.open(path).convert('RGB'))

def load_label(path,ignorebackground=False):
	label=np.array(Image.open(path).convert('L'))
	if ignorebackground:
		label[label==0]=IGNORE_INDEX
	return label

def image_to_tensor(image):
	'''HxWx3 uint8 -> normalized 3xHxW float tensor'''
	return torch.from_numpy(((image.astype(np.float32)-MEAN)/STD).transpose(2,0,1).copy())

class TileDataset(torch.utils.data.Dataset):
	'''image/label pairs, randomly cropped to crop=(h,w) and augmented if augment'''
	def __init__(self,pairs,crop=None,augment=False,ignorebackground=False):
		self.pairs=pairs
		self.crop=crop
		self.augment=augment
		self.ignorebackground=ignorebackground

	def __len__(self):
		return len(self.pairs)

	def __getitem__(self,i):
		image=load_image(self.pairs[i][0])
		label=load_label(self.pairs[i][1],self.ignorebackground)
		if self.crop:
			h,w=self.crop
			y=np.random.randint(0,image.shape[0]-h+1)
			x=np.random.randint(0,image.shape[1]-w+1)
			image=image[y:y+h,x:x+w]
			label=label[y:y+h,x:x+w]
		if self.augment: # nadir imagery: flips and 90 degree rotations
			if np.random.rand()<0.5:
				image,label=image[:,::-1],label[:,::-1]
			if np.random.rand()<0.5:
				image,label=image[::-1],label[::-1]
			if image.shape[0]==image.shape[1]:
				k=np.random.randint(4)
				image,label=np.rot90(image,k),np.rot90(label,k)
			image=np.clip(image*np.random.uniform(0.8,1.2)\
				+np.random.uniform(-20,20),0,255)
		return image_to_tensor(image),torch.from_numpy(label.astype(np.int64))

def crop_size(pairs,multiple=32):
	'''largest crop that fits all training images and the network'''
	h=min(Image.open(p[0]).size[1] for p in pairs)
	w=min(Image.open(p[0]).size[0] for p in pairs)
	if h<multiple or w<multiple:
		raise ValueError("Images need to be at least %dx%d pixels" % (multiple,multiple))
	return (h//multiple*multiple,w//multiple*multiple)

@torch.no_grad()
def predict(model,image,device,ignorebackground=False,multiple=32):
	'''class id per pixel of an HxWx3 uint8 image'''
	x=image_to_tensor(image).unsqueeze(0).to(device)
	h,w=x.shape[2:]
	pad_h=(-h)%multiple
	pad_w=(-w)%multiple
	x=F.pad(x,(0,pad_w,0,pad_h),mode='reflect')
	logits=model(x)[0,:,:h,:w]
	if ignorebackground: # background was not trained
		logits[0]=-float('inf')
	return logits.argmax(0).cpu().numpy().astype(np.uint8)

def confusion_matrix(pred,label,num_classes):
	'''rows: true class, columns: predicted class. Ignored pixels are skipped.'''
	valid=label!=IGNORE_INDEX
	return np.bincount(num_classes*label[valid].astype(np.int64)+pred[valid],
		minlength=num_classes**2).reshape(num_classes,num_classes)

def scores(cm,classes):
	'''per-class IoU, precision and recall; mean IoU over classes present in the labels'''
	tp=np.diag(cm).astype(np.float64)
	support=cm.sum(1)
	predicted=cm.sum(0)
	with np.errstate(divide='ignore',invalid='ignore'):
		iou=tp/(support+predicted-tp)
		precision=tp/predicted
		recall=tp/support
	present=support>0
	perclass=[{'class':name,'iou':iou[i],'precision':precision[i],'recall':recall[i],
		'pixels':int(support[i])} for i,name in enumerate(classes) if present[i]]
	return {'miou':float(np.mean(iou[present])) if present.any() else float('nan'),
		'accuracy':float(tp.sum()/max(cm.sum(),1)),
		'classes':perclass}

def format_scores(result):
	lines=["%-40s %7s %9s %7s %12s" % ('class','IoU','precision','recall','pixels')]
	for c in result['classes']:
		lines.append("%-40s %7.3f %9.3f %7.3f %12d" %
			(c['class'][:40],c['iou'],c['precision'],c['recall'],c['pixels']))
	lines.append("mean IoU: %.3f   pixel accuracy: %.3f" % (result['miou'],result['accuracy']))
	return "\n".join(lines)

def write_scores(path,result):
	clean=lambda v: None if isinstance(v,float) and np.isnan(v) else v
	result=dict(result,classes=[{k:clean(v) for k,v in c.items()} for c in result['classes']])
	with open(path,'w') as f:
		json.dump(result,f,indent=2,default=float)

def evaluate(model,pairs,classes,device,ignorebackground=False):
	model.eval()
	cm=np.zeros((len(classes),len(classes)),dtype=np.int64)
	for image_path,label_path in pairs:
		pred=predict(model,load_image(image_path),device,ignorebackground)
		cm+=confusion_matrix(pred,load_label(label_path,ignorebackground),len(classes))
	return scores(cm,classes)
