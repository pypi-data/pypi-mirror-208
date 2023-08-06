import torch
import torch.nn as nn


def DataParallel(model, verbose: bool=True):
	"""
	This function evaluates the number of GPUs available, and if more than one are found/available,
		then it call DataParallel.
	:param model: The model to convert if necessary.
	:param verbose: Display how many GPUs were found?
	:return: The same model if a single GPU was found, else nn.DataParallel(model).
	"""
	if torch.cuda.device_count() > 1:
		if verbose:
			print("Using", torch.cuda.device_count(), "GPUs!")
		model = nn.DataParallel(model)
		return model
	return model


def SaveStateDict(model, path: str, verbose: bool=True):
	"""
	This function saves the model state dictionary.
	:param model: The model to save.
	:param path: The path to the file that will contain the model.
	:param verbose: If True, it will say if everything went well.
	"""
	if torch.cuda.device_count() > 1:
		torch.save(model.module.state_dict(), path)
	else:
		torch.save(model.state_dict(), path)
	if verbose:
		print("Model successfully saved as: " + path)
