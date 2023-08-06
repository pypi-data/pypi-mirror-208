import glob
import imageio
import numpy
import os

import numpy as np
import skimage.io as skio
import sys
import tifffile
import time

from . import ImageTools as imTools
from tifffile import TiffWriter

from PIL import Image
Image.MAX_IMAGE_PIXELS = None



# ----------------------------------------------------- Tools -----------------------------------------------------
def FindImages(DirPath: str, Extensions: list=["png", "PNG", "tif", "TIF", "tiff", "TIFF"], NamesOnly: bool=True,
				verbose: bool=True) -> list:
	""" This function fins all the images in the given directory.
		Args:
			DirPath (str): The directory's path containing the images.
			Extensions (list): Only the images with these extensions will be read. Defaults to ["png", "PNG", "tif", "TIF", "tiff", "TIFF"].
			verbose (:obj:`bool`, optional): Use the verbose mode? Defaults to True.
		Returns:
			A list of all the image names in the given directory.
	"""
	list = []
	if NamesOnly:
		for ext in Extensions:
			list += [os.path.basename(x) for x in glob.glob(DirPath + "/*" + "." + ext)]
	else:
		for ext in Extensions:
			list += glob.glob(DirPath + "/*" + "." + ext)
	
	list.sort()
	
	if ( verbose ):
		print(" - %d images in %s" % (len(list), DirPath))
		sys.stdout.flush()

	return list


def ConcatenateDirectoryAndNames(DirPath: str, Names: list) -> list:
	""" This function concatenates the image names with the directory path.
		Args:
			DirPath (str): The directory's path.
			Names (list): The image names.
		Returns:
			The image names concatenated with the directory path.
	"""
	list = []
	for i in range(len(Names)):
		list.append(os.path.join(DirPath, Names[i]))
	return list






# ----------------------------------------------------- Load Images -----------------------------------------------------

def LoadImages(DirPath: str, ChannelFirst: bool=False, ReturnImagesList: bool=False, verbose: bool=True):
	""" This function reads all the images in a given directory.
		Args:
			DirPath (str): The directory's path containing the images.
			ChannelFirst (:obj:`bool`, optional): Put the image channel in first position? Defaults to False.
			ReturnImagesList (:obj:`bool`, optional): Is the images paths list returned along with the images? Defaults to False.
			verbose (:obj:`bool`, optional): Use the verbose mode? Defaults to True.
		Returns:
			A numpy.ndarray and the images paths list if ReturnImagesList is set to True.
	"""
	
	imlist = FindImages(DirPath, NamesOnly=False, verbose=verbose)
	
	if len(imlist) == 0:
		return
	
	return LoadImagesList(imlist, ChannelFirst=ChannelFirst, ReturnImagesList=ReturnImagesList, verbose=verbose)




def LoadImagesListInDirectory(DirPath: str, imList: list, ChannelFirst: bool=False, ReturnImagesList: bool=False, verbose: bool=True):
	""" This function reads all the images in a given directory.
		Args:
			DirPath (str): The directory's path containing the images.
			imList ([str]): The names of the images to read.
			ChannelFirst (:obj:`bool`, optional): Put the image channel in first position? Defaults to False.
			ReturnImagesList (:obj:`bool`, optional): Is the images paths list returned along with the images? Defaults to False.
			verbose (:obj:`bool`, optional): Use the verbose mode? Defaults to True.
		Returns:
			A numpy.ndarray and the images paths list if ReturnImagesList is set to True.
	"""
	
	imList = ConcatenateDirectoryAndNames(DirPath, imList)

	return LoadImagesList(imList, ChannelFirst=ChannelFirst, ReturnImagesList=ReturnImagesList, verbose=verbose)




def LoadImagesList(imList: list, ChannelFirst: bool=False, ReturnImagesList: bool=False, verbose: bool=True):
	""" This function reads all the images in a given directory.
		Args:
			imList ([str]): The full paths of the images to read.
			ChannelFirst (:obj:`bool`, optional): Put the image channel in first position? Defaults to False.
			ReturnImagesList (:obj:`bool`, optional): Is the images paths list returned along with the images? Defaults to False.
			verbose (:obj:`bool`, optional): Use the verbose mode? Defaults to True.
		Returns:
			A numpy.ndarray and the images paths list if ReturnImagesList is set to True.
	"""
	nbImages = len(imList)
	dataset = numpy.ndarray(shape=nbImages, dtype=object)

	#channels = -1
	image_index = 0
	errors = []
	for image_file in imList:
		try:
			image = imageio.imread(image_file).astype(float)
			
			#if channels < 0: # Done each time for the UnitTests that contain multiple types of images.
			w, h, channels, f = imTools.Dimensions(image)
			
			if channels == 1:
				if ChannelFirst == True:
					dataset[image_index] = image[numpy.newaxis, :, :]
				else:
					dataset[image_index] = image[:, :, numpy.newaxis]
			else:
				if ChannelFirst == True:
					dataset[image_index] = numpy.moveaxis(image, -1, 0)
				else:
					dataset[image_index] = image

			image = dataset[image_index] # ???????

			image_index += 1
		except IOError as e:
			print("Could not read '%s': %s - it\'s ok, skipping." % (image_file, e))
			sys.stdout.flush()
			errors.append(image_file)

	
	if verbose:
		print("\tLoaded: %d images, %d error(s)." % (image_index, len(errors)))
	
	if image_index < len(dataset):
		dataset = dataset[0: image_index]
		for err in errors:
			imList.remove(err)

	if verbose:
		print("\tFinal: %d images." % len(dataset))
		dim, text = FindDimensionsRange(dataset, True)
		print("\tDimensions: ", text)
		a, b, c, d, text = FindMinMaxRange(dataset, True)
		print("\tMin/Max: ", text)
		a, b, c, text = FindMeans(dataset, True)
		print("\tMean: ", text)
		a, b, c, text = FindStds(dataset, True)
		print("\tStd: ", text)

	sys.stdout.flush()
	
	if ReturnImagesList:
		return dataset, imList
	else:
		return dataset




def FindMinMaxRange(Dataset, Text: bool=False):
	length = Dataset.shape[0]
	minima = numpy.ndarray(length, dtype=float)
	maxima = numpy.ndarray(length, dtype=float)

	for i in range(length):
		minima[i] = Dataset[i].min()
		maxima[i] = Dataset[i].max()

	min_minima = round(minima.min(), 3)
	max_minima = round(minima.max(), 3)
	min_maxima = round(maxima.min(), 3)
	max_maxima = round(maxima.max(), 3)

	if Text:
		if length == 1 or min_minima == max_minima:
			textmin = str(min_minima)
		else:
			textmin = str(min_minima) + ", " + str(max_minima)
		
		if length == 1 or min_maxima == max_maxima:
			textmax = str(min_maxima)
		else:
			textmax = str(min_maxima) + ", " + str(max_maxima)
		
		text = "[" + textmin + "] / [" + textmax + "]"
		return min_minima, max_minima, min_maxima, max_maxima, text

	return min_minima, max_minima, min_maxima, max_maxima


def FindMeans(Dataset, Text: bool=False):
	length = Dataset.shape[0]
	means = numpy.ndarray(length, dtype=float)

	for i in range(length):
		means[i] = Dataset[i].mean()

	min = round(means.min(), 3)
	max = round(means.max(), 3)
	mean = round(means.mean(), 3)

	if Text:
		text = str(mean)
		if length != 1 and min != max:
			text += " [" + str(min) + ", " + str(max) + "]"
		return mean, min, max, text

	return mean, min, max


def FindStds(Dataset, Text:bool=False):
	length = Dataset.shape[0]
	stds = numpy.ndarray(length, dtype=float)

	for i in range(length):
		stds[i] = Dataset[i].std()

	min = round(stds.min(), 3)
	max = round(stds.max(), 3)
	mean = round(stds.mean(), 3)

	if Text:
		text = str(mean)
		if length != 1 and min != max:
			text += " [" + str(min) + ", " + str(max) + "]"
		return mean, min, max, text

	return mean, min, max


def FindDimensionsRange(Dataset, Text: bool=False):
	shape = Dataset[0].shape
	dimensions = numpy.ndarray(shape=(len(shape)*2), dtype=int)

	index = 0
	for i in range(0, len(shape)):
		dimensions[index] = dimensions[index+1] = shape[i]
		index += 2

	for i in range(1, len(Dataset)):
		shape = Dataset[i].shape

		index = 0
		for i in range(0, len(shape)):
			if shape[i] < dimensions[index]:
				dimensions[index] = shape[i]
			if dimensions[index+1] < shape[i]:
				dimensions[index+1] = shape[i]
			index += 2

	if Text:
		text = ""
		for i in range(0, len(dimensions), 2):
			if i == 0: separator = ""
			else: separator = "x"
			if dimensions[i] == dimensions[i+1]:
				text += separator + str(dimensions[i])
			else:
				text += separator + "[" + str(dimensions[i]) + ", " + str(dimensions[i+1]) + "]"
		return dimensions, text

	return dimensions










# ------------------------------------------------------- Read -------------------------------------------------------
def ReadOld(path: str, ChannelFirst: bool=True, verbose: bool=True):
	""" This function reads a single image.
		Args:
			path (str): The full path of the image to read.
			ChannelFirst (:obj:`bool`, optional): Put the image channel in first position? Defaults to False.
			verbose (:obj:`bool`, optional): Use the verbose mode? Defaults to True.
		Returns:
			A numpy.ndarray.
	"""

	if verbose:
		print("Reading image '" + path + "'...", end='')
	
	image = None
	
	try:
		image = imageio.imread(path).astype(float)
		
		w, h, channels, f = imTools.Dimensions(image)
		
		if channels == 1:
			if ChannelFirst:
				image = image[numpy.newaxis, :, :]
			else:
				image = image[:, :, numpy.newaxis]
		else:
			if ChannelFirst:
				image = numpy.moveaxis(image, -1, 0)
	except IOError as e:
		print("\nCould not read '%s': %s." % (path, e))
		sys.stdout.flush()
		return None

	if verbose:
		print(" shape=" + str(image.shape) + ", successfully.")
		sys.stdout.flush()
	
	return image


def Read(path: str, Library: str="PIL", Channel: str=None, verbose: bool=True):
	""" This function reads a single image using different available libraries.
		Args:
			path (str): The full path of the image to read.
			Library (str): Which library should be used to read the image? Default to PIL.
			Channel (str): What should be the poistion of the color channel. Defaults to None, so nothing will change.
			verbose (bool): Use the verbose mode? Defaults to True.
		Returns:
			A numpy.ndarray.
	"""
	library = Library.lower()
	if library not in {"pil", "skimage", "imageiov2", "imageiov3"}:
		raise Exception("Library not supported: '" + Library +
						"'. Expected PIL, SKimage, ImageIOv2, or ImageIOv3 (not case sensitive).")
	
	if Channel is not None:
		channel = Channel.lower()
		if channel not in {"first", "last"}:
			raise Exception("Channel value not supported: '"+Channel+"'. Expected First or Last (not case sensitive).")
	
	if verbose:
		print("Reading image '" + path + "'... ", end='')
	
	try:
		image = None
		if library == "pil":
			image = numpy.array(Image.open(path))
		elif library == "imageiov2":
			image = imageio.v2.imread(path)
		elif library == "imageiov3":
			image = imageio.v3.imread(path)
		elif library == "skimage":
			image = skio.imread(path)
		else:
			raise Exception("library not supported: '" + library + "'. Must not occur.")
		#print(image.shape)
	except IOError as e:
		print("\nCould not read '%s': %s." % (path, e))
		sys.stdout.flush()
		return None
	
	if Channel is not None:
		if channel == "first":
			image = imTools.AddMoveChannels(image, True)
		elif channel == "last":
			image = imTools.AddMoveChannels(image, False)
		else:
			raise Exception("Unknown Channel value: '" + library + "'. Must not occur.")
	
	if verbose:
		print(" shape=" + str(image.shape) + ", successfully.")
		sys.stdout.flush()
	
	return image






# -------------------------------------------------------- Save --------------------------------------------------------

def WriteBasic(Array, ChannelFirst: bool, name: str):
	""" This function save an array as an image.
		Args:
			Array : The array to save.
			ChannelFirst (bool): Is the image channel in first position?
			name (str): The image name.
	"""
	
	if ChannelFirst:
		width, height, channels = Array.shape[2], Array.shape[1], Array.shape[0]
	else:
		width, height, channels = Array.shape[1], Array.shape[0], Array.shape[2]

	if channels == 1:
		image = Image.new('L', (width, height))
		pixels = image.load()
		if ChannelFirst:
			for y in range(height):
				for x in range(width):
					pixels[x, y] = int(Array[0, y, x])
		else:
			for y in range(height):
				for x in range(width):
					pixels[x, y] = int(Array[y, x, 0])

	else:
		image = Image.new('RGB', (width, height))
		pixels = image.load()
		if ChannelFirst:
			for y in range(height):
				for x in range(width):
					pixels[x, y] = (int(Array[0, y, x]), int(Array[1, y, x]), int(Array[2, y, x]))
		else:
			for y in range(height):
				for x in range(width):
					pixels[x, y] = (int(Array[y, x, 0]), int(Array[y, x, 1]), int(Array[y, x, 2]))

	image.save(name, "PNG")










def Write(Array, ChannelFirst: bool, Name: str, FloatEncoding: bool=False):
	""" This function save an array as an image encoded in PNG if the max value is lower or equal to 65535, TIF otherwise.
		Args:
			Array : The array to save.
			ChannelFirst (bool): Is the image channel in first position?
			Name (str): The image name.
	"""
	
	if ChannelFirst and 2 < len(Array.shape) and 1 < Array.shape[0]: # Multiple channels first, so move them to the end.
		Array = numpy.moveaxis(Array, 0, -1)
	
	if ChannelFirst and 1 == Array.shape[0]: # 2D image
		Array = Array[0]

	if not ChannelFirst and len(Array.shape) == 3 and Array.shape[2] == 1:
		Array = Array.squeeze()
	
	name = (Name + '.')[:-1]
	max = Array.max()
	
	if not FloatEncoding:
		if max <= 255.0:
			encoding = "uint8"
			name = name.replace('.tif', '.png').replace('.TIF', '.png').replace('.tiff', '.png').replace('.TIFF', '.png')
		elif max <= 65535.0:
			encoding = "uint16"
			name = name.replace('.tif', '.png').replace('.TIF', '.png').replace('.tiff', '.png').replace('.TIFF', '.png')
		else:
			encoding = "uint32"
			name = name.replace('.png', '.tif').replace('.PNG', '.tif')
	else:
		encoding = "float32"
		name = name.replace('.png', '.tif').replace('.PNG', '.tif')
	
	image = Image.fromarray(Array.astype(encoding))
	image.save(name)





def _getExtension(name):
	assert name is not None
	return "" if name.endswith(".ome.tif") or name.endswith(".ome.tiff") or name.endswith(".ome.tf2") or \
				name.endswith(".ome.tf8") or name.endswith(".ome.btf") else ".ome.tif"



def WriteOMETIF(Stack, Path: str, BigTiff: bool=False):
	assert Stack is not None
	ext = _getExtension(Path)
	tifffile.imwrite(Path+ext, Stack, ome=True, bigtiff=BigTiff)



def WriteOMETIFfull(Stack, Path: str, BigTiff: bool=True, ChannelNames: str=None, photometric: str='minisblack',
					PixelSize: int=None, PixelUnit: str='µm', SubResolutions: int=2, TileSize: int=512,
					CreatePyramid: bool=False):
	assert Stack is not None
	ext = _getExtension(Path)
	
	if isinstance(Stack, list):
		channels = len(Stack)
		if CreatePyramid:
			Stack = np.stack(Stack)
	else:
		_, _, channels, _ = imTools.Dimensions(Stack)
	
	if ChannelNames is None: # None, so creating an artificial one.
		ChannelNames = ["Channel {}".format(i) for i in range(channels)]
	
	if PixelUnit == 'cm':
		resunit = 'CENTIMETER'
		PixelBase = 1e4
	elif PixelUnit == 'mm':
		resunit = 'MILLIMETER'
		PixelBase = 1e3
	elif PixelUnit == 'µm':
		resunit = 'MICROMETER'
		PixelBase = 1.
	else:
		raise Exception("Unsupported PixelUnit: '" + PixelUnit + "'. Expected: cm, mm, and µm.")
	
	with TiffWriter(Path, bigtiff=BigTiff) as tif:
		options = dict(photometric=photometric, tile=(TileSize, TileSize), resolutionunit=resunit)
		
		if PixelSize is not None:
			metadata = {
				'axes': 'CYX',
				'SignificantBits': 10,
				'PhysicalSizeX': PixelSize,
				'PhysicalSizeXUnit': PixelUnit,
				'PhysicalSizeY': PixelSize,
				'PhysicalSizeYUnit': PixelUnit,
				'Channel': {'Name': ChannelNames},
				'Plane': {'PositionX': [0.0] * 16, 'PositionXUnit': [PixelUnit] * 16}
				}
		else:
			metadata = {
				'axes': 'CYX',
				'SignificantBits': 10,
				'Channel': {'Name': ChannelNames},
				'Plane': {'PositionX': [0.0] * 16, 'PositionXUnit': [PixelUnit] * 16}
				}
			PixelSize = 1
		
		tif.write(Stack, subifds=SubResolutions, resolution=(PixelBase/PixelSize, PixelBase/PixelSize),
					metadata=metadata, **options)
		
		if CreatePyramid:
			# write pyramid levels. In production use resampling to generate sub-resolution images
			for level in range(SubResolutions):
				mag = 2 ** (level + 1)
				tif.write(Stack[:, ::mag, ::mag], subfiletype=1,
							resolution=(PixelBase/mag/PixelSize, PixelBase/mag/PixelSize), **options)
			# add a thumbnail image as a separate series. It is recognized by QuPath as an associated image
			thumbnail = (Stack[0, ::8, ::8] >> 2)  #.astype('uint8')
			tif.write(thumbnail, metadata={'Name': 'thumbnail'})




