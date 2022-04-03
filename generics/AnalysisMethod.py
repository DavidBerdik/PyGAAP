from abc import ABC, abstractmethod, abstractproperty
import math

import backend.Histograms as histograms
from importlib import import_module

from extra.modules.analysis_method_example import analysis_method_example

external_modules = {
	"extra.modules.analysis_method_example": None,
	"extra.modules.am_sklearn_naive_bayes": None,
}
# external imports must use "backend.import_external"
for mod in external_modules:
	external_modules[mod] = import_module(mod)

# An abstract AnalysisMethod class.
class AnalysisMethod(ABC):
	distance = None
	_variable_options = dict()
	_global_parameters = dict()
	
	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()	
		self._global_parameters = self._global_parameters

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
		return "Computes one centroid per Author.\nCentroids are the average relative frequency of events over all documents provided.\ni=1 to n ΣfrequencyIn_i(event)."

class CrossEntropy(AnalysisMethod):
	mode="author"
	_NoDistanceFunction_ = True
	_histograms = None
	_histogramsNp = None
	_variable_options = {"mode": {"default": 0, "type": "OptionMenu", "options": ["author", "document"]}}
	_multiprocessing_score = 1

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


class exampleExternalAM(AnalysisMethod):
	_NoDistanceFunction_ = True
	var = 1
	_variable_options = {"var": {"default": 0, "type": "OptionMenu", "options": [1, 3, 5, 6, 10, 12]}}

	def __init__(self):
		self._module = external_modules["extra.modules.analysis_method_example"].analysis_method_example()
		self.var = 1

	def unwrap(self):
		return self._module

	def train(self, known_docs):
		return None
	
	def analyze(self, unknownDocument):
		return 0 
	
	def displayDescription():
		return "Example external analysis method"

	def displayName():
		return "Example external AM"

# class sklearnNaiveBayes(AnalysisMethod):
# 	_NoDistanceFunction_ = True
# 	features_limit = 1000
# 	_variable_options = {"features_limit": {"default": 0, "type": "OptionMenu", "options": [1000, 2000, 3000, 4000]}}

# 	def __init_(self):
# 		self._module = external_modules["extra.modules.am_sklearn_naive_bayes"].sklearn_naive_bayes()

# 	def unwrap(self):
# 		return self._module
	
# 	def train(self, feature_set):
# 		self._module.max_features = self.features_limit
# 		results = self._module.train(feature_set)
	
# 	def analyze(self, unknown_doc_feature_set):
# 		self._module.max_features = self.features_limit
# 		results = self._module.predict(unknown_doc_feature_set)
	
# 	def displayDescription():
# 		return "Naive Bayes classifier with CountVectorizer using scikit-learn"
	
# 	def displayName():
# 		return "Naive Bayes (scikit-learn)"


