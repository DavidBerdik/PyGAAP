from abc import ABC, abstractmethod
import backend.Histograms as histograms

# if an anlysis method does not allow a distance function to be set, add a attribute called _NoDistanceFunction_ and set it to True.
# It's okay to omit _NoDistanceFunction_ if it would be set to False.
'''
Changes: added NoDistanceFunctionTest.
'''


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

	@abstractmethod
	def displayDescription():
		'''Returns the description of the method.'''
		pass
		
	def setDistanceFunction(self, distance):
		'''Sets the distance function to be used by the analysis driver.'''
		self.distance = distance
		
class CentroidDriver(AnalysisDriver):
	authorHistograms = None
	
	def train(self, knownDocuments):
		'''Get a mean normalized histogram for each known author.'''
		self.authorHistograms = histograms.generateKnownDocsMeanHistograms(histograms.generateKnownDocsNormalizedHistogramSet(knownDocuments))
		
	def analyze(self, unknownDocument):
		'''Compare a normalized histogram of unknownDocument against the normalized known document histograms and return a dictionary of distances.'''
		results = dict()
		for author, knownHist in self.authorHistograms.items():
			results[author] = self.distance.distance(histograms.normalizeHistogram(histograms.generateAbsoluteHistogram(unknownDocument)), knownHist)
		return results
	
	def displayName():
		return "Centroid Driver"

	def displayDescription():
		return "Computes one centroid per Author.\nCentroids are the average relitive frequency of events over all docuents provided.\ni=1 to n ΣfrequencyIn_i(event)."

class NoDistanceFunctionTest(AnalysisDriver):
	_NoDistanceFunction_=True
	def train(self): pass
	def analyze(self): pass
	def displayName(): return "No Distance Function Test"
	def displayDescription(): return "An empty method to test disabling of the distance function listbox."