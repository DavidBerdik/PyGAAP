from abc import ABC, abstractmethod
import backend.Histograms as histograms


# An abstract AnalysisMethod class.
class AnalysisMethod(ABC):
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
		
class CentroidDriver(AnalysisMethod):
	_authorHistograms = None
	
	def train(self, knownDocuments):
		'''Get a mean normalized histogram for each known author.'''
		self._authorHistograms = histograms.generateKnownDocsMeanHistograms(histograms.generateKnownDocsNormalizedHistogramSet(knownDocuments))
		
	def analyze(self, unknownDocument):
		'''Compare a normalized histogram of unknownDocument against the normalized known document histograms and return a dictionary of distances.'''
		results = dict()
		for author, knownHist in self._authorHistograms.items():
			results[author] = self.distance.distance(histograms.normalizeHistogram(histograms.generateAbsoluteHistogram(unknownDocument)), knownHist)
		return results
	
	def displayName():
		return "Centroid Driver"

	def displayDescription():
		return "Computes one centroid per Author.\nCentroids are the average relitive frequency of events over all docuents provided.\ni=1 to n ΣfrequencyIn_i(event)."

class NoDistanceFunctionTest(AnalysisMethod):
	_NoDistanceFunction_=True
	def train(self): pass
	def analyze(self): return 0
	def displayName(): return "No Distance Function Test"
	def displayDescription(): return "An empty method to test disabling of the distance function listbox."

class ADwithparameter(AnalysisMethod):
	test_param1=4
	test_param2=10
	_variable_options={"test_param1": list(range(7)), "test_param2": list(range(9, 12))}
	_variable_GUItype={"test_param1": "OptionMenu", "test_param2": "OptionMenu"}
	def train(self): pass
	def analyze(self): return 0
	def displayName(): return "test AD w params"
	def displayDescription(): return "An empty method to test the GUI parameter display."
