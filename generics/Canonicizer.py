from abc import ABC, abstractmethod

# An abstract Canonicizer class.
class Canonicizer(ABC):
	# Input is original text and output is canonicized text in the form of a character list.
	@abstractmethod
	def process(self, procText):
		pass
		
	# Returns the display name for the given canonicizer.
	@abstractmethod
	def displayName(self):
		pass