from abc import ABC, abstractmethod

# An abstract Canonicizer class.
class Canonicizer(ABC):
	# Input is original text and output is canonicized text in the form of a character array.
	def process(self, procText):
		pass
		
	# Returns the display name for the given canonicizer.
	def displayName(self):
		pass