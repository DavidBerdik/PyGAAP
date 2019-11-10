from abc import ABC, abstractmethod
from nltk import ngrams
from nltk.tokenize import word_tokenize

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
		nltkRawOutput = list(ngrams(procText, self.n)) # This gives us a list of tuples.
		# Make the list of tuples in to a list of character fragments in the form of strings.
		formattedOutput = [''.join(val) for val in nltkRawOutput]
		return formattedOutput
	
	def displayName():
		return "Character NGrams"
	
	def setParams(self, params):
		'''Sets the n parameter (length) for the Character N-Gram Event Driver. params is a list. '''
		self.n = params[0]
		
class WhitespaceDelimitedWordEventDriver(EventDriver):
	'''Event Driver for Whitespace-Delimited Words'''
	
	def createEventSet(self, procText):
		'''Returns a list of words where a word is considered a whitespace-delimited unit.'''
		return procText.split()
		
	def displayName():
		return "Words (Whitespace-Delimited)"
		
class NltkWordTokenizerEventDriver(EventDriver):
	'''Event Driver for using the NLTK Word Tokenizer.'''
	
	def createEventSet(self, procText):
		'''Returns a list of words as defined by the NLTK Word Tokenizer.'''
		return word_tokenize(procText)
		
	def displayName():
		return "Words (NLTK Tokenizer)"