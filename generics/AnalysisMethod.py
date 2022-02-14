from abc import ABC, abstractmethod, abstractproperty
import math
import backend.Histograms as histograms

# An abstract AnalysisMethod class.
class AnalysisMethod(ABC):
	distance = None
	_variable_options = dict()
	
	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()	
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

class CrossEntropy(AnalysisMethod):
	mode="author"
	_NoDistanceFunction_ = True
	_histograms = None
	_histogramsNp = None
	_variable_options = {"mode": {"default": 0, "type": "OptionMenu", "options": ["author", "document"]}}

	def train(self, knownDocuments):
		if self.mode == "author":
			# authors -> mean histograms
			self._histograms = histograms.generateKnownDocsMeanHistograms(histograms.generateKnownDocsNormalizedHistogramSet(knownDocuments))
			#self._histogramsNp = {author:np.asarray(list(docHistogram.items())) for (author,docHistogram) in self._histograms.items()}
			# ^^ goes into the histogram list and change mean histograms into numpy arrays
		elif self.mode == 'document':
			# authors -> list of histograms
			self._histograms = histograms.generateKnownDocsNormalizedHistogramSet(knownDocuments)
			#self._histogramsNp = {author:[np.asarray(list(docHistogram.items())) for docHistogram in listOfHistograms] for (author,listOfHistograms) in self._histograms.items()}
			# ^^ goes into the list of histograms and individually change all histograms of all authors into numpy arrays
	def analyze(self, unknownDocument):
		# unknownDocument is a single doc, type Document.
		results=dict()
		unknownDocHistogram: dict = histograms.normalizeHistogram(histograms.generateAbsoluteHistogram(unknownDocument))
		#unknownDocHistogramNp = np.asarray(list(unknownDocHistogram.items()))
		results = dict()
		if self.mode == "author":
			for author in self._histograms:
				authorResult = 0 # numerial result for an author (mean histogram)
				for item in self._histograms[author]:
					if unknownDocHistogram.get(item) != None:
						authorResult -= self._histograms[author][item] * math.log(unknownDocHistogram[item])
				results[author] = authorResult

		elif self.mode == "document":
			for author in self._histograms:
				for doc in self._histograms[author]:
					docResult = 0 # numerical result for a single document
					for item in doc:
						if unknownDocHistogram.get(item) != None:
							docResult -= self._histograms[author][doc][item] * math.log(unknownDocHistogram[item])
					results[doc] = docResult

		return results
	
	def displayDescription():
		return "Discrete cross Entropy."
	
	def displayName():
		return "Cross Entropy"