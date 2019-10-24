from abc import ABC, abstractmethod

# An abstract DistanceFunction class.
class DistanceFunction(ABC):
	@abstractmethod
	def distance(self, unknownHistogram, knownHistogram):
		'''Input is the unknown and known histograms and output is the resulting distance calculation.'''
		pass
		
	@abstractmethod
	def displayName():
		'''Returns the display name for the given distance function.'''
		pass