import FiReTiTiPyLib.IO.IOColors as Colors
import torch



def getDevice(cuda: bool=None, verbose: bool=True):
	"""
	This function returns the cuda device (torch.device).
	:param cuda: Try to use Cuda?
	:param verbose: If True, the function will displau the findings and a warning if cuda is not used/found.
	:return: The device to use.
	"""
	if cuda is None:
		device = "cuda" if torch.cuda.is_available() else "cpu"
	else:
		device = torch.device("cuda" if cuda else "cpu")
	if verbose:
		warning = '\n' if str(device) == 'cuda' else Colors.Colors.RED + "\nWARNING - " + Colors.Colors.RESET
		print(warning + "Device = " + str(device) + "\n")
	return device
