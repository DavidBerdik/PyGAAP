from generics.EventDriver import EventDriver
from nltk.util import ngrams

class CharacterNGramEventDriver(EventDriver):
	n = 2
	
	def createEventSet(self, procText):
		'''Returns a list containing the desired character n-grams.'''
		nltkRawOutput = list(ngrams(procText, n)) # This gives us a list of tuples.
		# Make the list of tuples in to a list of character fragments in the form of strings.
		formattedOutput = [''.join(val) for val in nltkRawOutput]
		return formattedOutput
	
	def displayName(self):
		return "Character NGrams"
	
	def setParam(self, params):
		'''Sets the n parameter (length) for the Character N-Gram Event Driver. params is a list. '''
		self.n = params[0]