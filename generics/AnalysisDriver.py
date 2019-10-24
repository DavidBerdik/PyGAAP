from abc import ABC, abstractmethod

# An abstract AnalysisDriver class.
class AnalysisDriver(ABC):
	@abstractmethod
	def train(self, knownDocuments):
		'''Train a model on the knownDocuments.'''
		pass
		
	@abstractmethod
	def analyze(self, unknownDocument):
		'''Analyze unknownDocument'''
		pass

	@abstractmethod
	def displayName(self):
		'''Returns the display name for the given analysis method.'''
		pass