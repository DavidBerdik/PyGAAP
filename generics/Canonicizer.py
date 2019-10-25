from abc import ABC, abstractmethod

# An abstract Canonicizer class.
class Canonicizer(ABC):
	@abstractmethod
	def process(self, procText):
		'''Input is original text and output is canonicized text.'''
		pass
		
	@abstractmethod
	def displayName():
		'''Returns the display name for the given canonicizer.'''
		pass
		
class NormalizeWhitespace(Canonicizer):
	def process(self, procText):
		'''Convert procText in to a string where all whitespace characters are the same.'''
		return ' '.join(procText.split())

	def displayName():
		return "Normalize Whitespace"