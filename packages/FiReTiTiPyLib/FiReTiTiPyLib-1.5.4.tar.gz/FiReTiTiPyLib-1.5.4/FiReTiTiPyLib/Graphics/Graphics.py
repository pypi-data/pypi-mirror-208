import matplotlib.pyplot as plt
import numpy as np
import scipy
import seaborn

"""
Options:
	:param linewidth: The width of the line around each point/dot.
	:param hue: Colored according to a variable.
	:param size: Size of points according to a variable.
	:param style: Type/style of point according to a variable
"""



def nbRows(length: int, nCols: int):
	return int(length / nCols) + (0 if length % nCols == 0 else 1)


def Plots(Type: str, Features, FeatureNames, Class: str, FigSize: int=6, nCols: int=3, nRows: int=0,
			Save: str=None, dpi=150, Show: bool=False, **kwargs):
	"""
	This function uses a simple seaborn stripplot to plot each element with a dot, and sorted by class on the X axis.
	:param Type: The type of plot to perform: Violin or Strip.
	:param Features: The Pandas DataFrame containing the features.
	:param FeatureNames: The nome of the columns to display/plot.
	:param Class: The name of the column containing the classes.
	:param FigSize: Which size for each figure. Defaults to 6.
	:param nCols: Number of figures per column. Defaults to 3.
	:param nRows: Number of figures per row. Defaults to 0, so this number will be automatically computed.
	:param Save: If not None, then the figure will be saved.
	:param dpi: Dots Pe Inch (DPI). Defaults to 150.
	:param Show: If True, then the figure will be shown. Defaults to False.
	:return:
	"""
	type = Type.lower()
	if type not in ["violin", "strip"]:
		raise Exception("Unsupported/Unrecognize type: '" + Type + "'. Expected: Violin or Strip.")
	
	length = len(FeatureNames)
	if nRows <= 0:
		nRows = nbRows(length, nCols)
	
	figs, axs = plt.subplots(ncols=nCols, nrows=nRows, figsize=(FigSize * nCols, int(FigSize * length / nCols)))
	
	for i, feature in enumerate(FeatureNames, start=0):
		if type == "strip":
			plot = seaborn.stripplot(y=feature, x=Class, data=Features, ax=axs[int(i / nCols), i % nCols], **kwargs)
		elif type == "violin":
			plot = seaborn.violinplot(y=feature, x=Class, data=Features, ax=axs[int(i / nCols), i % nCols], **kwargs)
		else:
			raise Exception("Must not occur!")
	
	if Save is not None:
		plt.savefig(Save + " - " + Class + ".pdf", format="pdf", dpi=dpi)
		plt.savefig(Save + " - " + Class + ".png", dpi=dpi)
	if Show:
		plt.show()
	plt.cla()



def StripPlots(Features, FeatureNames, Class: str, FigSize: int=6, nCols: int=3, nRows: int=0,
				Save: str=None, dpi=150, Show: bool=False, **kwargs):
	"""
	This function uses a simple seaborn stripplot to plot each element with a dot, and sorted by class on the X axis.
	:param Features: The Pandas DataFrame containing the features.
	:param FeatureNames: The nome of the columns to display/plot.
	:param Class: The name of the column containing the classes.
	:param FigSize: Which size for each figure. Defaults to 6.
	:param nCols: Number of figures per column. Defaults to 3.
	:param nRows: Number of figures per row. Defaults to 0, so this number will be automatically computed.
	:param Save: If not None, then the figure will be saved.
	:param dpi: Dots Pe Inch (DPI). Defaults to 150.
	:param Show: If True, then the figure will be shown. Defaults to False.
	:return:
	"""
	Plots("Strip", Features, FeatureNames, Class, FigSize, nCols, nRows, Save, dpi, Show, **kwargs)



def ViolinPlots(Features, FeatureNames, Class: str, FigSize: int=6, nCols: int=3, nRows: int=0,
				Save: str=None, dpi=150, Show: bool=False, **kwargs):
	"""
	This function uses a simple seaborn stripplot to plot each element with a dot, and sorted by class on the X axis.
	:param Features: The Pandas DataFrame containing the features.
	:param FeatureNames: The nome of the columns to display/plot.
	:param Class: The name of the column containing the classes.
	:param FigSize: Which size for each figure. Defaults to 6.
	:param nCols: Number of figures per column. Defaults to 3.
	:param nRows: Number of figures per row. Defaults to 0, so this number will be automatically computed.
	:param Save: If not None, then the figure will be saved.
	:param dpi: Dots Pe Inch (DPI). Defaults to 150.
	:param Show: If True, then the figure will be shown. Defaults to False.
	:return:
	"""
	Plots("Violin", Features, FeatureNames, Class, FigSize, nCols, nRows, Save, dpi, Show, **kwargs)



def DualScatterPlot(Features, Feature1: str, Feature2: str, Density: bool=False, Save: str=None,
					dpi=150, Show: bool=False, **kwargs):
	"""
	This function draws a dual scatterplot of two variable: Feature 1 vs Feature 2
	:param Features: The Pandas DataFrame containing the features.
	:param Feature1: The name of the first feature.
	:param Feature2: The name of the first feature.
	:param Density: Add density color to the plot?
	:param Save: If not None, then the figure will be saved.
	:param dpi: Dots Pe Inch (DPI). Defaults to 150.
	:param Show: If True, then the figure will be shown. Defaults to False.
	:return:
	"""
	X = Features[[Feature1, Feature2]]
	
	if Density:
		values = np.vstack([X[Feature1], X[Feature2]])
		kernel = scipy.stats.gaussian_kde(values)(values)
		plot = seaborn.scatterplot(data=X, x=Feature1, y=Feature2, c=kernel, **kwargs)
	else:
		plot = seaborn.scatterplot(data=X, x=Feature1, y=Feature2, **kwargs)
	
	if Save is not None:
		plt.savefig(Save + " - " + Feature1 + " vs " + Feature2 + ".pdf", format="pdf", dpi=dpi)
		plt.savefig(Save + " - " + Feature1 + " vs " + Feature2 + ".png", dpi=dpi)
	if Show:
		plt.show()
	plt.cla()



def AllDualScatterPlots(Features, FeatureNames, Feature: str, FigSize: int=6, nCols: int=3, nRows: int=0,
						Density: bool=False, Save: str=None, dpi=150, Show: bool=False, **kwargs):
	"""
	This function plots all the the given feature versus all the available features.
	:param Features: The Pandas DataFrame containing the features.
	:param FeatureNames: The nome of all the features to display/plot.
	:param Feature: The main feature to plot all the other features against.
	:param FigSize: Which size for each figure. Defaults to 6.
	:param nCols: Number of figures per column. Defaults to 3.
	:param nRows: Number of figures per row. Defaults to 0, so this number will be automatically computed.
	:param Density: Add density color to the plot?
	:param Save: If not None, then the figure will be saved.
	:param dpi: Dots Pe Inch (DPI). Defaults to 150.
	:param Show: If True, then the figure will be shown. Defaults to False.
	:return:
	"""
	length = len(FeatureNames)
	
	if nRows <= 0:
		nRows = nbRows(length, nCols)
	
	figs, axs = plt.subplots(ncols=nCols, nrows=nRows, figsize=(FigSize * nCols, int(FigSize * length / nCols)))
	
	for j, feat in enumerate(FeatureNames, start=0):
		if feat != Feature:
			X = Features[[Feature, feat]]
			
			if Density:
				values = np.vstack([X[Feature], X[feat]])
				kernel = scipy.stats.gaussian_kde(values)(values)
				plot = seaborn.scatterplot(data=X, x=Feature, y=feat, c=kernel, cmap="viridis",
											ax=axs[int(j / nCols), j % nCols], **kwargs)
			else:
				plot = seaborn.scatterplot(data=X, x=Feature, y=feat, cmap="viridis",
											ax=axs[int(j / nCols), j % nCols], **kwargs)
	
	if Save is not None:
		plt.savefig(Save + " - " + Feature + " vs All.pdf", format="pdf", dpi=dpi)
		plt.savefig(Save + " - " + Feature + " vs All.png", dpi=dpi)
	if Show:
		plt.show()
	plt.cla()
	