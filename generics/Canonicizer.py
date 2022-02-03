from abc import ABC, abstractmethod
import re

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

	@abstractmethod
	def displayDescription():
		'''Returns the display description for the canonicizer.'''
		
class NormalizeWhitespace(Canonicizer):
	def process(self, procText):
		'''Convert procText in to a string where all whitespace characters are the same.'''
		return ' '.join(procText.split())

	def displayName():
		return "Normalize Whitespace"

	def displayDescription():
		return "Converts all whitespace characters (newline, space and tab) to a single space.  Uses Java Character.isWhitespace for classification."

class UnifyCase(Canonicizer):
	def process(self, procText):
		"""Convert procText to lower case"""
		return procText.lower()
	
	def displayName():
		return "Unify Case"

	def displayDescription():
		return "Converts all text to lower case."

class StripPunctuation(Canonicizer):
	def process(self, procText):
		"""Gets rid of punctuation characters"""
		return ''.join([char for char in procText if char not in ",.?!\"'`;:-()&$"])
	
	def displayDescription():
		return 'Strip all punctuation characters (,.?!"\'`;:-()&$) from the text.'

	def displayName():
		return "Strip Punctuation"

class StripNumbers(Canonicizer):
	def process(self, procText):
		"""Converts each digit string to a single zero."""
		regex_match=re.compile("0+")
		procText=''.join(["0" for char in procText if char in "0123456789"])
		return re.subn(regex_match, "0", procText)[0]

	def displayDescription():
		return "Converts each digit strings to a single 0"

	def displayName():
		return "Strip Numbers"

class PunctuationSeparator(Canonicizer):
	def process(self, procText):
		"""Adds whitespaces before and after punctuations."""
		return ''.join([" "+char+" " if char in ",.?!\"'`;:-()&$" else char for char in procText])
	
	def displayDescription():
		return "Adds whitespaces before and after punctuations."
	
	def displayName():
		return "Punctuation Separator"

class StripAlphanumeric(Canonicizer):
	def process(self, procText):
		"""Strips all non-whitespace, non-punctuation marks."""
		return ''.join([char for char in procText if char in " ,.?!\"'`;:-()&$"])

	def displayDescription():
		return "Strips all non-whitespace, non-punctuation marks. i.e. leaves only white spaces and punctuation marks."
	
	def displayName():
		return "Strip Alpha-numeric"

class StripNullCharacters(Canonicizer):
	def process(self, procText):
		return ''.join([char for char in procText if char!="\0"])

	def displayDescription():
		return "Strips all 0x00 from the text."
	
	def displayName():
		return "Strip Null Characters"

