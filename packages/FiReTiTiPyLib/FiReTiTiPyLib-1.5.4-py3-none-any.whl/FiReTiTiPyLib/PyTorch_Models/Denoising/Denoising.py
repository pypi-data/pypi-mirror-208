import sys

from torch import nn


class DenoiseNet(nn.Module):
	"""
	This class defines a denoising model.

	Args:
		Inputs (int): The number of input image or the number of colors in the input image.
		Depth (int): The model depth, so the number of layers/levels. Defaults to 24.
		FeatureMaps (int): The number of feature maps per layer/level. Defaults to 64.
		KernelSize (int): The convolution kernel size. Defaults to 3.
		Activations (str): The type of activation layer to use after each convolution. "relu" and "elu" are supported, defaults to "relu".
		BatchNormalization (bool): Use batch normalization? Defaults to False.
		DropOut (float): The drop out probability. Must be in range [0,1], and defaults to 0.
		Outputs (int): The number of predicted maps. Defaults to 1.
	"""
	
	def __init__(self, Inputs: int=1, Depth: int=24, FeatureMaps: int=64, KernelSize: int=3, Activations: str="relu",
				BatchNormalization: bool=None, DropOut: float=0.0, Outputs: int=1):
		super(DenoiseNet, self).__init__()
		
		if DropOut < 0.0 or 1.0 < DropOut:
			raise Exception("DropOut value must be in range [0,1].")
		
		if not (Activations == "relu" or Activations == "elu"):
			raise Exception("Unknown activation")
		
		self.FeatureMaps = FeatureMaps
		self.Depth = Depth
		
		self.padding = int(KernelSize/2)
		self.FirstResConv = nn.Conv2d(Inputs, Outputs, KernelSize, padding=self.padding)
		
		self.MainConv = nn.ModuleList()
		self.MainConv.append(nn.Conv2d(Inputs, FeatureMaps, KernelSize, padding=self.padding))
		
		self.Activations = nn.ModuleList()
		if Activations == "relu":
			self.Activations.append(nn.ReLU())
		elif Activations == "elu":
			self.Activations.append(nn.ELU())
		
		if BatchNormalization is not None:
			self.BN = nn.ModuleList()
			self.BN.append(nn.BatchNorm2d(FeatureMaps-1, affine=BatchNormalization))
		else:
			self.BN = None
		
		if 0.0 < DropOut:
			self.DO = nn.ModuleList()
			self.DO.append(nn.Dropout2d(p=DropOut))
		else:
			self.DO = None
		
		for d in range(1, self.Depth-2):
			self.MainConv.append(nn.Conv2d(FeatureMaps-1, FeatureMaps, KernelSize, padding=self.padding))
			if BatchNormalization is not None:
				self.BN.append(nn.BatchNorm2d(FeatureMaps-1, affine=BatchNormalization))
			if self.DO is not None:
				self.DO.append(nn.Dropout2d(p=DropOut))
			if Activations == "relu":
				self.Activations.append(nn.ReLU())
			elif Activations == "elu":
				self.Activations.append(nn.ELU())
		
		for d in range(0, 2):
			self.MainConv.append(nn.Conv2d(FeatureMaps-1, FeatureMaps, KernelSize, padding=self.padding))
			if BatchNormalization is not None:
				self.BN.append(nn.BatchNorm2d(FeatureMaps-1, affine=BatchNormalization))
			if 0.0 < DropOut:
				self.DO.append(nn.Dropout2d(p=DropOut))
			self.Activations.append(nn.Identity())#nn.Linear(FeatureMaps-1, FeatureMaps))



	def forward(self, x):
		result = x.clone() + self.FirstResConv(x)
		
		for d in range(0, self.Depth):
			x = self.MainConv[d](x)
			result += x[:, self.FeatureMaps-1:self.FeatureMaps, :, :].clone()  # Last feature map added to the result.
			x = x[:, 0:self.FeatureMaps-1, :, :] #N-1 features maps to model the noise
			if self.BN is not None:
				x = self.BN[d](x)
			if self.DO is not None:
				x = self.DO[d](x)
			x = self.Activations[d](x)
		
		return result
