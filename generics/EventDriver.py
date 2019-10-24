from abc import ABC, abstractmethod

# An abstract EventDriver class.
class EventDriver(ABC):
	@abstractmethod
	def displayName():
		'''Returns the display name for the given event driver.'''
		pass
		
	@abstractmethod
	def createEventSet(self, procText):
		'''Returns a list containing the resulting event set.'''
		pass
		
	@abstractmethod
	def setParams(self, params):
		'''Accepts a list of parameters and assigns them to the appropriate variables.'''
		
		
class CharacterNGramEventDriver(EventDriver):
	'''Event Driver for Character N-Grams'''
	n = 2
	
	def createEventSet(self, procText):
		'''Returns a list containing the desired character n-grams.'''
		nltkRawOutput = list(ngrams(procText, n)) # This gives us a list of tuples.
		# Make the list of tuples in to a list of character fragments in the form of strings.
		formattedOutput = [''.join(val) for val in nltkRawOutput]
		return formattedOutput
	
	def displayName():
		return "Character NGrams"
	
	def setParam(self, params):
		'''Sets the n parameter (length) for the Character N-Gram Event Driver. params is a list. '''
		self.n = params[0]