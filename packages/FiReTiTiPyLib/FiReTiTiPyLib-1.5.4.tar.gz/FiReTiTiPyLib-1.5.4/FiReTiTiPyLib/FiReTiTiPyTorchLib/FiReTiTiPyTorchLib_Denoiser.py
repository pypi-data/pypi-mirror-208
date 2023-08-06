import FiReTiTiPyLib.ImagesIO as imIO
import FiReTiTiPyLib.ImageTools as imTools
import FiReTiTiPyLib.FiReTiTiPyTorchLib.FiReTiTiPyTorchLib_Segmentator as Segmentator
import numpy
import os
import random
import sys
import torch

from horology import timed





class Denoiser(object):
	
	def __init__(self, verbose: bool=True):
		self.__Reset__()
		
		self.verbose = verbose
		
		self.rand = random.Random()
	
	
	def __Reset__(self):
		pass
	
	
	
	
	@timed
	def Denoise(self, dataset, Model, nInputs: int, CropSize: int, BorderEffectSize: int,
					BatchSize: int, Device, Normalizer, ResultsDirPath: str):
		""" This function segment all the images in the given directory using the given model.
			Args:
				dataset: The PyTorch Dataset to list all the images..
				Model (object): The model to use.
				nInputs (int): Number of inputs. Usually 3 for NRRN and 1 for DenoiseNet.
				CropSize (int): The crop dimension. Windows/crops of dimensions (CropSize,CropSize) will be generated and segmented.
				BorderEffectSize (int): The size of the border effect.
				BatchSize (int): the batch size.
				Device: PyTorch device (gpu or cpu)
				Normalizer: the image normalizer/denormalizer to use.
				ResultsDirPath (str): The directory to save the segmented images.
		"""
		
		if CropSize <= 0:
			raise Exception("CropSize <= 0.")
		
		if CropSize <= 2 * BorderEffectSize:
			raise Exception("CropSize <= 2 x BorderEffectSize.")
		
		os.makedirs(ResultsDirPath, exist_ok=True)
		
		nbImages = dataset.__len__()
		
		if self.verbose:
			addon = 1 if nInputs == 1 else 2
			print(" - %d images to denoise.\n\n" % (nbImages+addon))
			sys.stdout.flush()
		
		if nInputs == 1:
			for i in range(0, nbImages):
				name = dataset.image_filenames[i]
				if self.verbose:
					print(" - Denoising image: '" + str(name) + str("'"))
				
				image, imnext = dataset.__getitem__(i)
				
				Normalizer.NormalizeTensor(image)
				
				result = self._Denoise1_(image, Model, BatchSize, CropSize, BorderEffectSize, Device)
				
				Normalizer.DenormalizeArray(result)
				name = os.path.basename(name)
				imIO.Write(result, True, ResultsDirPath + "/" + name.replace('.tiff', '.png').replace('.tif', '.png'))
			
			Normalizer.NormalizeTensor(imnext)
			result = self._Denoise1_(imnext, Model, BatchSize, CropSize, BorderEffectSize, Device)
			Normalizer.DenormalizeArray(result)
			name = os.path.basename(dataset.next_filenames[i])
			imIO.Write(result, True, ResultsDirPath + "/" + name.replace('.tiff', '.png').replace('.tif', '.png'))
		elif nInputs == 3:
			for i in range(0, nbImages):
				name = dataset.image_filenames[i]
				if self.verbose:
					print(" - Denoising image: '" + str(name) + str("'"))
				
				imprev, image, imnext = dataset.__getitem__(i)
				
				Normalizer.NormalizeTensor(imprev)
				Normalizer.NormalizeTensor(imnext)
				Normalizer.NormalizeTensor(image)
				
				result = self._Denoise3_(imprev, image, imnext, Model, BatchSize, CropSize, BorderEffectSize, Device)
				
				Normalizer.DenormalizeArray(result)
				name = os.path.basename(name)
				imIO.Write(result, True, ResultsDirPath + "/" + name.replace('.tiff', '.png').replace('.tif', '.png'))
			
			imprev, image, imnext = dataset.__getitem__(0)
			Normalizer.NormalizeTensor(image)
			Normalizer.NormalizeTensor(imprev)
			result = self._Denoise3_(image, imprev, image, Model, BatchSize, CropSize, BorderEffectSize, Device)
			Normalizer.DenormalizeArray(result)
			name = os.path.basename(dataset.previous_filenames[0])
			imIO.Write(result, True, ResultsDirPath + "/" + name.replace('.tiff', '.png').replace('.tif', '.png'))
			
			imprev, image, imnext = dataset.__getitem__(dataset.__len__()-1)
			Normalizer.NormalizeTensor(image)
			Normalizer.NormalizeTensor(imnext)
			result = self._Denoise3_(image, imnext, image, Model, BatchSize, CropSize, BorderEffectSize, Device)
			Normalizer.DenormalizeArray(result)
			name = os.path.basename(dataset.next_filenames[dataset.__len__()-1])
			imIO.Write(result, True, ResultsDirPath + "/" + name.replace('.tiff', '.png').replace('.tif', '.png'))
		else:
			raise Exception("Number of inputs not supported. Expected: 1 or 3.")


	def _Denoise1_(self, image, Model, BatchSize: int, CropSize: int, BorderEffectSize: int, Device):
		bes = BorderEffectSize
		csmbes = CropSize - BorderEffectSize
		width, height, channels, first = imTools.Dimensions(image)
		
		result = numpy.ndarray(shape=(height, width), dtype=numpy.float32)
		
		batch = numpy.ndarray(shape=(BatchSize, channels, CropSize, CropSize), dtype=numpy.float32)
		
		it = Segmentator.SingleIterator(image, CropSize, BorderEffectSize, True, verbose=self.verbose)
		coordinates = []
		try:
			while True:  # Get all the coordinates.
				X, Y = next(it.PositionsGenerator)
				coordinates.append((X, Y))
		except StopIteration:
			pass
		
		length = len(coordinates)
		pos = 0
		while pos < length:
			start = pos
			pos += BatchSize
			end = min(pos, length)
			
			for c, index in zip(range(start, end), range(end - start)):
				X, Y = coordinates[c]
				batch[index] = image[:, Y:Y+CropSize, X:X+CropSize]
			
			torchbatch = torch.as_tensor(batch, device=Device, dtype=torch.float32)
			
			predictions = Model(torchbatch)  # Model at work!!!
			
			for c, index in zip(range(start, end), range(end - start)): # Saving results in the right places.
				X, Y = coordinates[c]
				if X == 0:
					if Y == 0:
						result[Y:Y+CropSize, X:X+CropSize] = predictions[index].detach().cpu().numpy()
					elif Y + CropSize == height:
						result[Y+bes:Y+CropSize, X:X+CropSize] = predictions[index, :, bes:CropSize, :].detach().cpu().numpy()
					else:
						result[Y+bes:Y+csmbes, X:X+CropSize] = predictions[index, :, bes:csmbes, :].detach().cpu().numpy()
				elif Y == 0:
					if X+CropSize == width:
						result[Y:Y+CropSize, X+bes:X+CropSize] = predictions[index, :, :, bes:CropSize].detach().cpu().numpy()
					else:
						result[Y:Y+CropSize, X+bes:X+csmbes] = predictions[index, :, :, bes:csmbes].detach().cpu().numpy()
				elif X+CropSize == width:
					if Y+CropSize == height:
						result[Y+bes:Y+CropSize, X+bes:X+CropSize] = predictions[index, :, bes:CropSize, bes:CropSize].detach().cpu().numpy()
					else:
						result[Y+bes:Y+csmbes, X+bes:X+CropSize] = predictions[index, :, bes:csmbes, bes:CropSize].detach().cpu().numpy()
				elif Y+CropSize == height:
					result[Y+bes:Y+CropSize, X+bes:X+csmbes] = predictions[index, :, bes:CropSize, bes:csmbes].detach().cpu().numpy()
				else:
					result[Y+bes:Y+csmbes, X+bes:X+csmbes] = predictions[index, :, bes:csmbes, bes:csmbes].detach().cpu().numpy()
		return result

	
	def _Denoise3_(self, imprev, image, imnext, Model, BatchSize: int, CropSize: int, BorderEffectSize: int, Device):
		bes = BorderEffectSize
		csmbes = CropSize - BorderEffectSize
		width, height, channels, first = imTools.Dimensions(image)
		
		result = numpy.ndarray(shape=(height, width), dtype=numpy.float32)
		
		batchprev = numpy.ndarray(shape=(BatchSize, channels, CropSize, CropSize), dtype=numpy.float32)
		batch = numpy.ndarray(shape=(BatchSize, channels, CropSize, CropSize), dtype=numpy.float32)
		batchnext = numpy.ndarray(shape=(BatchSize, channels, CropSize, CropSize), dtype=numpy.float32)
		
		it = Segmentator.SingleIterator(image, CropSize, BorderEffectSize, True, verbose=self.verbose)
		coordinates = []
		try:
			while True:  # Get all the coordinates.
				X, Y = next(it.PositionsGenerator)
				coordinates.append((X, Y))
		except StopIteration:
			pass
		
		length = len(coordinates)
		pos = 0
		while pos < length:
			start = pos
			pos += BatchSize
			end = min(pos, length)
			
			for c, index in zip(range(start, end), range(end - start)):
				X, Y = coordinates[c]
				batchprev[index] = imprev[:, Y:Y + CropSize, X:X + CropSize]
				batch[index] = image[:, Y:Y + CropSize, X:X + CropSize]
				batchnext[index] = imnext[:, Y:Y + CropSize, X:X + CropSize]
			
			torchbatchprev = torch.as_tensor(batchprev, device=Device, dtype=torch.float32)
			torchbatch = torch.as_tensor(batch, device=Device, dtype=torch.float32)
			torchbatchnext = torch.as_tensor(batchnext, device=Device, dtype=torch.float32)
			
			x = torch.cat((torchbatchprev, torchbatch), dim=1) # concat the 2 images on the channel dim => (batch,2,256,256)
			y = torch.cat((torchbatchnext, torchbatch), dim=1)
			
			xpred = Model(x) # Model at work!!!
			ypred = Model(y)
			predictions = (xpred+ypred) / 2.0
			
			for c, index in zip(range(start, end), range(end - start)):  # Saving results in the right places.
				X, Y = coordinates[c]
				if X == 0:
					if Y == 0:
						result[Y:Y + CropSize, X:X + CropSize] = predictions[index].detach().cpu().numpy()
					elif Y + CropSize == height:
						result[Y + bes:Y + CropSize, X:X + CropSize] = predictions[index, :, bes:CropSize, :].detach().cpu().numpy()
					else:
						result[Y + bes:Y + csmbes, X:X + CropSize] = predictions[index, :, bes:csmbes, :].detach().cpu().numpy()
				elif Y == 0:
					if X + CropSize == width:
						result[Y:Y + CropSize, X + bes:X + CropSize] = predictions[index, :, :, bes:CropSize].detach().cpu().numpy()
					else:
						result[Y:Y + CropSize, X + bes:X + csmbes] = predictions[index, :, :, bes:csmbes].detach().cpu().numpy()
				elif X + CropSize == width:
					if Y + CropSize == height:
						result[Y + bes:Y + CropSize, X + bes:X + CropSize] = predictions[index, :, bes:CropSize, bes:CropSize].detach().cpu().numpy()
					else:
						result[Y + bes:Y + csmbes, X + bes:X + CropSize] = predictions[index, :, bes:csmbes, bes:CropSize].detach().cpu().numpy()
				elif Y + CropSize == height:
					result[Y + bes:Y + CropSize, X + bes:X + csmbes] = predictions[index, :, bes:CropSize, bes:csmbes].detach().cpu().numpy()
				else:
					result[Y + bes:Y + csmbes, X + bes:X + csmbes] = predictions[index, :, bes:csmbes, bes:csmbes].detach().cpu().numpy()
		
		return result
	
