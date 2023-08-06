import numpy
import random
import torch





def ParallelCompose(Compose, Images):
	seed = numpy.random.randint(2147483647)  # make a seed with numpy generator
	Results = []
	for image in Images:
		random.seed(seed)  # apply this seed to img tranfsorms
		torch.manual_seed(seed)  # needed for torchvision 0.7
		Results.append(Compose(image))
	return Results
