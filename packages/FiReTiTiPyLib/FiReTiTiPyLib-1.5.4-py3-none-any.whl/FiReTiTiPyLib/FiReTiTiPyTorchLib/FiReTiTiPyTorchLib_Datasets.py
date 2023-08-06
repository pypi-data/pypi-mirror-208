import FiReTiTiPyLib.ImagesIO as ImagesIO
import FiReTiTiPyLib.FiReTiTiPyTorchLib.FiReTiTiPyTorchLib_Transformations as Transformations
import numpy
import random
import sys
import torch
import torch.utils.data as data
import torchvision.transforms.functional as TF

from natsort import humansorted
from os import listdir
from os.path import join





class MaskRCNN(object):

	def __init__(self, Generator, BatchSize: int, InputsNormalizers=None, EmptyOutput: bool=False,
					MinimumBoxSize: int=11, Safety: int=131):
		
		self.BatchSize = BatchSize
		self.EmptyOutput = EmptyOutput
		
		self.Safety = Safety
		
		self.MinimumBoxSize = MinimumBoxSize
		
		self.Dataset = Generator.PyTorchDataset(BatchSize, InputsNormalizers=InputsNormalizers, OutputsNormalizers=None)
		self.Item = self.Dataset.__getitem__



	def __getitem__(self, idx):
		count = 0
		while True:
			data = self.Item(idx)
			inputs, outputs = data['input'], data['output']
			
			if inputs.shape[0] == 1:
				inputs = numpy.tile(inputs, (3, 1, 1))
			else:
				inputs = inputs.squeeze()
			inputs = torch.as_tensor(inputs, dtype=torch.float32)
		
			obj_ids = numpy.unique(outputs) # Nuclei are encoded as different labels.
			obj_ids = obj_ids[1:] # Remove 0 which is the background.
			
			masks = outputs == obj_ids[:, None, None] # Split the color-encoded mask into a set of binary masks
		
			nbObjects = len(obj_ids)
			if self.EmptyOutput == False and nbObjects == 0: # Should not happen because handled by the generator.
				raise Exception("Number of objects equal 0. Not supported (yet)!")
			
			delete = [] # get bounding box coordinates for each mask
			boxes = []
			for i in range(nbObjects):
				pos = numpy.where(masks[i])
				xmin = numpy.min(pos[1])
				xmax = numpy.max(pos[1])
				ymin = numpy.min(pos[0])
				ymax = numpy.max(pos[0])
				if xmax < xmin+self.MinimumBoxSize or ymax < ymin+self.MinimumBoxSize: # Remove small boxes.
					delete.append(i)
				else:
					boxes.append([xmin, ymin, xmax, ymax])
			
			if self.EmptyOutput == True or 0 < len(boxes):
				boxes = torch.as_tensor(boxes, dtype=torch.float32) # Convert everything into a torch.Tensor
				labels = torch.ones((nbObjects-len(delete),), dtype=torch.int64) # There is only one class
				if 0 < len(delete):
					masks = numpy.delete(masks, delete, axis=0)
				masks = torch.as_tensor(masks, dtype=torch.uint8)
		
				image_id = torch.tensor([idx])
				
				isSomething = torch.zeros((nbObjects-len(delete),), dtype=torch.int64) # Suppose all instances are not objects
				
				if nbObjects-len(delete) == 0: # Specific format required for no boxes.
					boxes = boxes.reshape(-1, 4)
					area = torch.as_tensor(0, dtype=torch.float32)
				else:
					area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
				
				Target = {}
				Target["boxes"] = boxes
				Target["labels"] = labels
				Target["masks"] = masks
				Target["image_id"] = image_id
				Target["area"] = area
				Target["isSomething"] = isSomething
				
				return inputs, Target
			
			count += 1
			if self.Safety <= count:
				raise Exception("Impossible to produced a non empty output for image index " + str(idx))


	def __len__(self):
		return self.Dataset.__len__()








class SuperMaskRCNN(object):

	def __init__(self, Dataset: int, EmptyOutput: bool=False, MinimumBoxSize: int=11, Safety: int=131):
		
		self.EmptyOutput = EmptyOutput
		
		self.Safety = Safety
		
		self.MinimumBoxSize = MinimumBoxSize
		
		self.Dataset = Dataset
		self.Item = self.Dataset.__getitem__



	def __getitem__(self, idx):
		count = 0
		while True:
			data = self.Item(idx)
			inputs, outputs = data['input'], data['output']
		
			if inputs.shape[0] == 1:
				inputs = numpy.tile(inputs, (3, 1, 1))
			else:
				inputs = inputs.squeeze()
			inputs = torch.as_tensor(inputs, dtype=torch.float32)
		
			obj_ids = numpy.unique(outputs) # Nuclei are encoded as different labels.
			obj_ids = obj_ids[1:] # Remove 0 which is the background.
			
			masks = outputs == obj_ids[:, None, None] # Split the color-encoded mask into a set of binary masks
		
			nbObjects = len(obj_ids)
			if self.EmptyOutput == False and nbObjects == 0: # Should not happen because handled by the generator.
				raise Exception("Number of objects equal 0. Not supported (yet)!")
			
			delete = [] # get bounding box coordinates for each mask
			boxes = []
			for i in range(nbObjects):
				pos = numpy.where(masks[i])
				xmin = numpy.min(pos[1])
				xmax = numpy.max(pos[1])
				ymin = numpy.min(pos[0])
				ymax = numpy.max(pos[0])
				if xmax < xmin+self.MinimumBoxSize or ymax < ymin+self.MinimumBoxSize: # Remove small boxes.
					delete.append(i)
				else:
					boxes.append([xmin, ymin, xmax, ymax])
			
			if self.EmptyOutput == True or 0 < len(boxes):
				boxes = torch.as_tensor(boxes, dtype=torch.float32) # Convert everything into a torch.Tensor
				labels = torch.ones((nbObjects-len(delete),), dtype=torch.int64) # There is only one class
				if 0 < len(delete):
					masks = numpy.delete(masks, delete, axis=0)
				masks = torch.as_tensor(masks, dtype=torch.uint8)
		
				image_id = torch.tensor([idx])
				
				isSomething = torch.zeros((nbObjects-len(delete),), dtype=torch.int64) # Suppose all instances are not objects
				
				if nbObjects-len(delete) == 0: # Specific format required for no boxes.
					boxes = boxes.reshape(-1, 4)
					area = torch.as_tensor(0, dtype=torch.float32)
				else:
					area = (boxes[:, 3] - boxes[:, 1]) * (boxes[:, 2] - boxes[:, 0])
				
				Target = {}
				Target["boxes"] = boxes
				Target["labels"] = labels
				Target["masks"] = masks
				Target["image_id"] = image_id
				Target["area"] = area
				Target["isSomething"] = isSomething
				
				return inputs, Target
			
			count += 1
			if self.Safety <= count:
				raise Exception("Impossible to produced a non empty output for image index " + str(idx))


	def __len__(self):
		return self.Dataset.__len__()










# ------------------------------------------------------- NRRN -------------------------------------------------------
class NRRN(data.Dataset):

	def __init__(self, images_dir, normalizer=None, nInputs: int=3, train: bool=True, datasetSize: int=-1,
						transformations=None, Debug: bool=False):
		super(NRRN, self).__init__()
		self.images_dir = images_dir
		self.nInputs = nInputs
		self.image_filenames = []
		self.next_filenames = []
		self.train = train
		self.normalizer = normalizer
		self.transformations = transformations
		self.Debug = Debug
		
		AllFiles = listdir(images_dir)
		AllImages = [x for x in AllFiles if _is_image_file(x)]
		Images = humansorted(AllImages)
		if self.Debug:
			print("Images:")
			print(*Images, sep='\n')
		
		if nInputs == 1:
			for x in range(0, len(Images)-1):
				self.image_filenames.append(join(images_dir, Images[x]))
				self.next_filenames.append(join(images_dir, Images[x+1]))
		elif nInputs == 3:
			self.previous_filenames = []
			for x in range(1, len(Images)-1):
				self.previous_filenames.append(join(images_dir, Images[x-1]))
				self.image_filenames.append(join(images_dir, Images[x]))
				self.next_filenames.append(join(images_dir, Images[x+1]))
		else:
			raise Exception("Parameter 'inputSize' must be 1 (single image for DenoiseNet) or 3 (triplets for NRRN).")
		
		if datasetSize == 0:
			raise Exception("The dataset size cannot be null.")
		elif 0 < datasetSize:
			indexes = list(range(len(self.image_filenames)))
			random.shuffle(indexes)
			indexes = indexes[:datasetSize]
			indexes.sort()
			tmp = [self.image_filenames[i] for i in indexes]
			self.image_filenames = tmp.copy()
			tmp.clear()
			tmp = [self.next_filenames[i] for i in indexes]
			self.next_filenames = tmp.copy()
			tmp.clear()
			if nInputs == 3:
				tmp = [self.previous_filenames[i] for i in indexes]
				self.previous_filenames = tmp.copy()
				tmp.clear()
			
		if self.Debug:
			for x in range(len(self.image_filenames)):
				if nInputs == 3:
					print(self.previous_filenames[x] + "   ", end='')
				print(self.image_filenames[x] + "   " + self.next_filenames[x])
	
	
	def __getitem__(self, index):
		# Input triplets
		previm = ImagesIO.Read(self.previous_filenames[index], Channel="First", verbose=False) if self.nInputs == 3\
																								else None
		image = ImagesIO.Read(self.image_filenames[index], Channel="First", verbose=False)
		nextim = ImagesIO.Read(self.next_filenames[index], Channel="First", verbose=False)
		
		if self.normalizer is not None: # Let's normalize
			if self.nInputs == 3:
				self.normalizer.Normalize(previm)
			self.normalizer.Normalize(image)
			self.normalizer.Normalize(nextim)
		
		previm = torch.as_tensor(previm, dtype=torch.float32) if self.nInputs == 3 else None # To tensors
		image = torch.as_tensor(image, dtype=torch.float32)
		nextim = torch.as_tensor(nextim, dtype=torch.float32)
		
		"""
		# Random crop
		i, j, h, w = Transformer.RandomCrop.get_params(image, output_size=(self.cropSize, self.cropSize))
		previm = TF.crop(previm, i, j, h, w) if self.inputSize == 3 else None
		image = TF.crop(image, i, j, h, w)
		nextim = TF.crop(nextim, i, j, h, w)
		
		if random.random() > 0.5: # Random horizontal flipping
			previm = TF.hflip(previm) if self.inputSize == 3 else None
			image = TF.hflip(image)
			nextim = TF.hflip(nextim)
		
		if random.random() > 0.5: # Random vertical flipping
			previm = TF.vflip(previm) if self.inputSize == 3 else None
			image = TF.vflip(image)
			nextim = TF.vflip(nextim)
		
		return previm, image, nextim
		"""
		
		if self.train and self.transformations is not None: # Transformations <=> Data Augmentation
			if self.nInputs == 3:
				results = Transformations.ParallelCompose(self.transformations, [previm, image, nextim])
				return results[0], results[1], results[2]
			else:
				results = Transformations.ParallelCompose(self.transformations, [image, nextim])
				return results[0], results[1]
		
		if self.nInputs == 3:
			return previm, image, nextim
		else:
			return image, nextim
		


	def __len__(self):
		return len(self.image_filenames)



def _is_image_file(filename: str): # Acquire image triplets and their ground truth
	return any(filename.lower().endswith(extension) for extension in [".png", ".jpg", ".jpeg", ".tif", ".tiff"])
