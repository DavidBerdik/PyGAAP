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
		
		# Populate dictionary of analysis methods.
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
			
	def _buildParamList(self, eventDriverString):
		'''Builds and returns a list of parameter values that will be passed to an EventDriver.'''
		eventDriverString = eventDriverString.split('|')[1:]
		params = []
		[params.append(int(param.split(':')[1])) for param in eventDriverString]
		return params