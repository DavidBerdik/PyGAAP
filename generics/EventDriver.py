from abc import ABC, abstractmethod

# An abstract EventDriver class.
class EventDriver(ABC):
	canonicizers = []
	
	def addCanonicizer(self, canonicizer):
		'''Adds the given canonicizer to the list of canonicizers.'''
		self.canonicizers.append(canonicizer)
		
	def removeCanonicizer(self, canonicizer):
		'''Removes the given canonicizer from the list of canonicizers.'''
		self.canonicizers.remove(canonicizer)
		
	def getCanonicizers(self)
		'''Returns the list of canonicizers.'''
		return self.canonicizers
		
	@abstractmethod
	def displayName(self):
		'''Returns the display name for the given event driver.'''
		pass
		
	@abstractmethod
	def createEventSet(self, procText):
		'''Returns a list containing the resulting event set.'''
		pass