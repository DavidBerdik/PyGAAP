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
	
	def __init__(self):
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