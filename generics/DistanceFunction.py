from abc import ABC, abstractmethod
import dictances as distances

# An abstract DistanceFunction class.
class DistanceFunction(ABC):

	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()
	@abstractmethod
	def distance(unknownHistogram, knownHistogram):
		'''Input is the unknown and known histograms and output is the resulting distance calculation.'''
		pass
		
	def displayName():
		'''Returns the display name for the given distance function.'''
		pass

	def displayDescription():
		pass

class BhattacharyyaDistance(DistanceFunction):
	def distance(unknownHistogram, knownHistogram):
		return distances.bhattacharyya(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Bhattacharyya Distance"
		
class ChiSquareDistance(DistanceFunction):
	def distance(unknownHistogram, knownHistogram):
		return distances.chi_square(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Chi Square Distance"
		
class CosineDistance(DistanceFunction):
	def distance(unknownHistogram, knownHistogram):
		return distances.cosine(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Cosine Distance"
		
class HistogramDistance(DistanceFunction):
	def distance(unknownHistogram, knownHistogram):
		return distances.euclidean(unknownHistogram, knownHistogram)
		
	def displayName():
		return "Euclidean/Histogram Distance"
	
	def displayDescription():
		return "Computes Euclidean distance."