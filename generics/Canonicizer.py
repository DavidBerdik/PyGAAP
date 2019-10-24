from abc import ABC, abstractmethod

# An abstract Canonicizer class.
class Canonicizer(ABC):
	@abstractmethod
	def process(self, procText):
		'''Input is original text and output is canonicized text in the form of a character list.'''
		pass
		
	@abstractmethod
	def displayName(self):
		'''Returns the display name for the given canonicizer.'''
		pass
		
class NormalizeWhitespace(Canonicizer):
	def process(self, procText):
		'''Convert procText in to a character list where all whitespace characters are the same.'''
		return list(' '.join(procText.split()))

	def displayName(self):
		return "Normalize Whitespace"