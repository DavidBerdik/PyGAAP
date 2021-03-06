from generics.Canonicizer import Canonicizer
from generics.EventDriver import EventDriver
from generics.AnalysisDriver import AnalysisDriver
from generics.DistanceFunction import DistanceFunction

class API:
	'''API class'''
	canonicizers = dict()
	eventDrivers = dict()
	analysisMethods = dict()
	distanceFunctions = dict()
	documents = []
	
	def __init__(self, documents):
		'''Build dictionaries of all the different parameters we can choose from.'''
		# Populate dictionary of canonicizers.
		for cls in Canonicizer.__subclasses__():
			self.canonicizers[cls.displayName()] = cls
		
		# Populate dictionary of event drivers.
		for cls in EventDriver.__subclasses__():
			self.eventDrivers[cls.displayName()] = cls
		
		# Populate dictionary of analysis methods.
		for cls in AnalysisDriver.__subclasses__():
			self.analysisMethods[cls.displayName()] = cls
		
		# Populate dictionary of distance functions.
		for cls in DistanceFunction.__subclasses__():
			self.distanceFunctions[cls.displayName()] = cls
			
		# Set a list of documents for processing.
		self.documents = documents
		
	def runCanonicizer(self, canonicizerString):
		'''Runs the canonicizer specified by the string against all documents.'''
		canonicizer = self.canonicizers.get(canonicizerString)()
		for doc in self.documents:
			doc.text = canonicizer.process(doc.text)
			
	def runEventDriver(self, eventDriverString):
		'''Runs the event driver specified by the string against all documents.'''
		eventDriver = self.eventDrivers.get(eventDriverString.split('|')[0])()
		eventDriver.setParams(self._buildParamList(eventDriverString))
		for doc in self.documents:
			doc.setEventSet(eventDriver.createEventSet(doc.text))
			
	def runAnalysis(self, analysisMethodString, distanceFunctionString):
		'''Runs the specified analysis method with the specified distance function and returns the results.'''
		analysis = self.analysisMethods.get(analysisMethodString)()
		
		# Set the distance function to be used by the analysis method.
		analysis.setDistanceFunction(self.distanceFunctions.get(distanceFunctionString))
		
		# Identify the unknown document in the set of documents. The unknown document's author field will be an empty string.
		unknownDoc = None
		for document in self.documents:
			if document.author == "":
				unknownDoc = document
				break
		knownDocs = self.documents.copy()
		knownDocs.remove(unknownDoc)
		
		# Use the analysis to train and return the results of performing the analysis.
		analysis.train(knownDocs)
		return unknownDoc, analysis.analyze(unknownDoc)
		
	def prettyFormatResults(self, canonicizers, eventDriver, analysisMethod, distanceFunc, unknownDoc, results):
		'''Returns a string of the results in a pretty, formatted structure.'''
		# Build a string the contains general information about the experiment.
		formattedResults = str(unknownDoc.title) + ' ' + str(unknownDoc.filepath) + "\nCanonicizers:\n"
		for canonicizer in canonicizers:
			formattedResults += '\t' + canonicizer + '\n'
		formattedResults += "Event Driver:\n\t" + eventDriver + "\nAnalysis Method:\n\t" + analysisMethod + " with " + distanceFunc + '\n'
		
		# Sort the dictionary in ascending order by distance values and build the results listing.
		orderedResults = {k: results[k] for k in sorted(results, key=results.get)}
		placement = 0
		prev = None
		for k, v in orderedResults.items():
			if prev == None or prev < v:
				placement += 1
				prev = v
			formattedResults += str(placement) + ". " + str(k) + ' ' + str(v) + '\n'
		
		return formattedResults
			
	def _buildParamList(self, eventDriverString):
		'''Builds and returns a list of parameter values that will be passed to an EventDriver.'''
		eventDriverString = eventDriverString.split('|')[1:]
		params = []
		[params.append(int(param.split(':')[1])) for param in eventDriverString]
		return params