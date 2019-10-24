from abc import ABC, abstractmethod

# An abstract EventDriver class.
class EventDriver(ABC):
	@abstractmethod
	def displayName(self):
		'''Returns the display name for the given event driver.'''
		pass
		
	@abstractmethod
	def createEventSet(self, procText):
		'''Returns a list containing the resulting event set.'''
		pass
		
	@abstractmethod
	def setParams(self, params):
		'''Accepts a list of parameters and assigns them to the appropriate variables.'''