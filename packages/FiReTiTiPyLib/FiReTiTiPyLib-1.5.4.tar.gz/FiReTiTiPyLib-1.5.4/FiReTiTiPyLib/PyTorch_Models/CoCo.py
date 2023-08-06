import glob
import json
import numpy as np
import os
import sys

from PIL import Image, ImageDraw
from shapely.geometry import Polygon, MultiPolygon # (pip install Shapely)
from skimage import measure





def _FindBoxes(labels):
	height, width = labels.shape
	boxes = {}
	for y in range(height):
		for x in range(width):
			label = int(labels[y][x])
			
			if label != 0:
				labelStr = str(label)
				box = boxes.get(labelStr)
			
				if box is None:
					boxes[labelStr] = {'Xmin': x, 'Xmax': x, 'Ymin': y, 'Ymax': y}
					box = boxes[labelStr]
			
				if x < box['Xmin']:
					box['Xmin'] = x
				elif box['Xmax'] < x:
					box['Xmax'] = x
			
				if y < box['Ymin']:
					box['Ymin'] = y
				elif box['Ymax'] < y:
					box['Ymax'] = y
	return boxes



def _FindObjects(labels, boxes, Simplify: float=0.0, PreserveTopology: bool=False):
	objects = []
	for key in boxes.keys():
		box = boxes[key]
		xmin = box['Xmin']
		xmax = box['Xmax']
		ymin = box['Ymin']
		ymax = box['Ymax']
		
		crop = labels[ymin:ymax+1, xmin:xmax+1].copy()
		
		dims = crop.shape
		intKey = int(key)
		for y in range(dims[0]): #crop = np.where(crop == key, crop, 0)
			for x in range(dims[1]):
				if crop[y][x] != intKey:
					crop[y][x] = 0
		
		crop = np.pad(crop, 1)
		
		polygons = []
		segmentations = []
		contours = measure.find_contours(crop, 0.5, positive_orientation='low')
		for contour in contours:
			for i in range(len(contour)):
				row, col = contour[i]
				contour[i] = (col+xmin-1, row+ymin-1)
			
			# Make a polygon and simplify it
			poly = Polygon(contour)
			if 0.0 < Simplify:
				poly = poly.simplify(Simplify, preserve_topology=PreserveTopology)
			polygons.append(poly)
			segmentation = np.array(poly.exterior.coords).ravel().tolist()
			for i in range(len(segmentation)):
				segmentation[i] = round(segmentation[i])
			segmentations.append(segmentation)
		
		# Combine the polygons to calculate the bounding box and area
		multi_poly = MultiPolygon(polygons)
		area = round(multi_poly.area)
		#x, y, max_x, max_y = multi_poly.bounds
		#width = round(max_x - x, Round)
		#height = round(max_y - y, Round)
		#bbox = (round(x, Round), round(y, Round), width, height)
		bbox = (xmin, ymin, xmax-xmin+1, ymax-ymin+1)
		
		objects.append({'label': int(key),
						'segmentation': segmentations,
						'bbox': bbox,
						'area': area})
		
	return objects



def SingleCategory(Images, Category: str, ResultDirPath: str, Simplify: float=0.0, PreserveTopology: bool=True,
					Draw: bool= True):
	"""
	Inspired from: https://www.immersivelimit.com/create-coco-annotations-from-scratch
	:param Images: The list of images pairs [{'Image': 'image1, 'Labels': 'labels1'}, ...]
	:param Category: The unique class name.
	:param ResultDirPath: Where to place the results.
	:param Simplify: Simplify the contours? No if the value is null. Default to 0.0
	:param PreserveTopology: Linked to the simplification. Default to True.
	:param Draw: Draw contours/ground truth? If True the results will be placed in the result directory.
	"""
	images = []
	annotations = []
	categories = [{'id': 0, 'name': Category}]
	
	imID = 0
	for im in Images:
		imagePath = im['Image']
		labelsPath = im['Labels']
		print("Processing: '" + imagePath + "', '" + labelsPath + "'")
		image = Image.open(imagePath)
		imWidth, imHeight = image.size
		width, height = image.size
		images.append({'file_name': imagePath, 'width': width, 'height': height, 'id': imID})
		if Draw:
			min, max = image.getextrema()
			if 255 < max:
				lut = [round(i / 256) for i in range(65536)]
				image = image.point(lut, 'L')
			image = image.convert("RGB")
			draw = ImageDraw.Draw(image)
		
		groundtruth = []
		labels = Image.open(labelsPath)
		labWidth, labHeight = labels.size
		if imWidth != labWidth or imHeight != labHeight:
			raise Exception("imWidth != labWidth or imHeight != labHeight")
		labels = np.array(labels)
		boxes = _FindBoxes(labels)
		objects = _FindObjects(labels, boxes, Simplify=Simplify, PreserveTopology=PreserveTopology)
		for obj in objects:
			groundtruth.append({'image_id': imID, 'id': obj['label'], 'segmentation': obj['segmentation'],
								'area': obj['area'], 'iscrowd': 0, 'bbox': obj['bbox'], 'category_id': 0})
			if Draw:
				for o in obj['segmentation']:
					draw.polygon(o, outline="yellow")
		annotations.append(groundtruth)
		
		if Draw:
			name = os.path.splitext(os.path.basename(imagePath))[0]
			name += "_GT.png"
			image.save(ResultDirPath + "/" + name)
		
		imID += 1
	
	
	with open(ResultDirPath + "/GroundTruth.json", 'w') as f:
		f.write("{'images': ".strip('"'))
		json.dump(images, f)
		f.write(",\n\n'annotations': ".strip('"'))
		json.dump(annotations, f)
		f.write(",\n\n'categories': ".strip('"'))
		json.dump(categories, f)
		f.write("}\n".strip('"'))





def _ListImages(Originals: str, Labels: str):
	originals = glob.glob(Originals + "/*.png")
	originals.sort()
	labels = glob.glob(Labels + "/*.tif")
	labels.sort()
	
	result = []
	for ori, lab in zip(originals, labels):
		result.append({'Image': ori, 'Labels': lab})
	return result





if __name__ == '__main__':
	"""images = [{'Image': '/Users/firetiti/Downloads/CyclicIF/MMtest/bottle_book.png',
				'Labels': '/Users/firetiti/Downloads/CyclicIF/MMtest/bottle_book_mask.png'},
			{'Image': '/Users/firetiti/Downloads/CyclicIF/MMtest/plant_book.png',
				'Labels': '/Users/firetiti/Downloads/CyclicIF/MMtest/plant_book_mask.png'}]"""
	path = "/Users/firetiti/Downloads/CyclicIF/IF Manual Segmentation/BR1506-A015/002 - Cropped/"
	images = _ListImages(path + "/Originals", path + "/Labels")
	#images = [{'Image': '/Users/firetiti/Downloads/CyclicIF/MMtest/BR1506-A015 - Scene 002.png',
	#			'Labels': '/Users/firetiti/Downloads/CyclicIF/MMtest/BR1506-A015 - Scene 002.tif'}]
	#print(images)
	#images = images[0:1]
	#print(images)
	SingleCategory(images, "Nuclei", "/Users/firetiti/Downloads/CyclicIF/MMtest/", Simplify=0.0)
