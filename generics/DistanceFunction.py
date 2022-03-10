from abc import ABC, abstractmethod
import dictances as distances
from importlib import import_module

external_modules = {}
# external imports must use "backend.import_external"
for mod in external_modules:
	external_modules[mod] = import_module(mod)

# An abstract DistanceFunction class.
class DistanceFunction(ABC):
	_global_parameters = dict()

	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()
		self._global_parameters = self._global_parameters
	@abstractmethod
	def distance(self, unknownHistogram, knownHistogram):
		'''Input is the unknown and known histograms and output is the resulting distance calculation.'''
		pass
		
	def displayName():
		'''Returns the display name for the given distance function.'''
		pass

	def displayDescription():
		pass

class BhattacharyyaDistance(DistanceFunction):
	def distance(self, unknownHistogram, knownHistogram):
		return distances.bhattacharyya(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Bhattacharyya Distance"
		
class ChiSquareDistance(DistanceFunction):
	def distance(self, unknownHistogram, knownHistogram):
		return distances.chi_square(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Chi Square Distance"
		
class CosineDistance(DistanceFunction):
	def distance(self, unknownHistogram, knownHistogram):
		return distances.cosine(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Cosine Distance"
		
class HistogramDistance(DistanceFunction):
	def distance(self, unknownHistogram, knownHistogram):
		return distances.euclidean(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Euclidean/Histogram Distance"
	
	def displayDescription():
		return "Computes Euclidean distance."