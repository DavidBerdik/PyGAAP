from abc import ABC, abstractmethod

# An abstract AnalysisDriver class.
class AnalysisDriver(ABC):
	distance = None
	
	@abstractmethod
	def train(self, knownDocuments):
		'''Train a model on the knownDocuments.'''
		pass
		
	@abstractmethod
	def analyze(self, unknownDocument):
		'''Analyze unknownDocument'''
		pass

	@abstractmethod
	def displayName():
		'''Returns the display name for the given analysis method.'''
		pass
		
	def setDistanceFunction(self, distance)
		'''Sets the distance function to be used by the analysis driver.'''
		self.distance = distance
