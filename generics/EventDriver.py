from abc import ABC, abstractmethod
from matplotlib.pyplot import eventplot
from nltk import ngrams
from nltk.tokenize import word_tokenize, sent_tokenize

'''
changes:
added __variable_options, __variable_GUItype to classes with class variables.
'''

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

	@abstractmethod
	def displayDescription():
		pass
		
# REFERENCE CLASS FOR PyGAAP GUI.
class CharacterNGramEventDriver(EventDriver):
	'''Event Driver for Character N-Grams'''
	n = 2
	_variable_options={"n": list(range(2, 8))} # for PyGAAP GUI to know which options to list/are valid
	_variable_GUItype={"n": "OptionMenu"}		# for PyGAAP GUI to know what kind of tkinter widget to use to set the variables. Can be "OptionMenu" or "Entry"
	
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

	def displayDescription(): # The text to display in PyGAAP GUI's description box.
		return "Groups of N successive characters (sliding window); N is given as a parameter."
	
		
class WhitespaceDelimitedWordEventDriver(EventDriver):
	'''Event Driver for Whitespace-Delimited Words'''
	
	def createEventSet(self, procText):
		'''Returns a list of words where a word is considered a whitespace-delimited unit.'''
		return procText.split()
		
	def displayName():
		return "Words (Whitespace-Delimited)"
	
	def setParams(self, params):
		'''This function is required, but does not do anything for this event driver.'''
		pass
		
	def displayDescription():
		return "Returns a list of words where a word is considered a whitespace-delimited unit."

class NltkWordTokenizerEventDriver(EventDriver):
	'''Event Driver for using the NLTK Word Tokenizer.'''
	
	def createEventSet(self, procText):
		'''Returns a list of words as defined by the NLTK Word Tokenizer.'''
		return word_tokenize(procText)
		
	def displayName():
		return "Words (NLTK Tokenizer)"
		
	def setParams(self, params):
		'''This function is required, but does not do anything for this event driver.'''
		pass

	def displayDescription():
		return "Word tokenizer using the Natural Language Took Kit's definition."
		
class SentenceEventDriver(EventDriver):
	'''Event Driver for getting sentences using the NLTK Sentence Tokenizer.'''
	
	def createEventSet(self, procText):
		'''Returns a list of sentences as defined by the NLTK Sentence Tokenizer.'''
		return sent_tokenize(procText)
		
	def displayName():
		return "Sentences"
		
	def setParams(self, params):
		'''This function is required, but does not do anything for this event driver.'''
		pass

	def displayDescription():
		return "Returns a list of sentences as defined by the NLTK Sentence Tokenizer."

class CharacterPositionEventDriver(EventDriver):
	'''Event Driver for letter positions. Only used on texts with delimited words (after canonicization).'''

	delimiter="<whitespace(s)>"
	_variable_options = {"delimiter": ["<whitespace(s)>", ", (comma)", ". (period)", "? (q. mark)", "! (excl. mark)", "& (ampersand)", "% (percent sign)", "$ (dollar sign)"]}
	_variable_GUItype = {"delimiter": "OptionMenu"}

	def createEventSet(self, procText):

		eventSet = []
		if self.delimiter == "<whitespace(s)>":
			splitText = procText.split()
		else:
			splitText = procText.split(self.delimiter[0])

		for word in splitText:
			eventSet += [str(word[letterIndex] + str(letterIndex)) for letterIndex in range(len(word))]
		print(eventSet)
		return eventSet

	def setParams(self, params):
		'''This function is required, but does not do anything for this event driver.'''
		pass
	
	def displayName():
		return "Character Position"

	def displayDescription():
		return "Converts delimited words into list of letters with their positions within the word.\nRecommended with the Cangjie canonicizer"