from abc import ABC, abstractmethod
from matplotlib.pyplot import eventplot
from nltk import ngrams
from nltk.tokenize import word_tokenize, sent_tokenize
import spacy
from importlib import import_module

external_modules = {}
# external imports must use "backend.import_external"
for mod in external_modules:
	external_modules[mod] = import_module(mod)


# An abstract EventDriver class.
class EventDriver(ABC):

	_global_parameters = dict()

	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()
		self._global_parameters = self._global_parameters

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
	_variable_options={"n": {"options": list(range(1, 21)), "default": 1, "type": "OptionMenu"}}
	# for PyGAAP GUI to know which options to list/are valid
		
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

	delimiter = "<whitespace(s)>"
	_variable_options = {"delimiter":
		{
			"options": ["<whitespace(s)>", ", (comma)", ". (period)", "; (semicolon)"],
			"type": "OptionMenu",
			"default": 0
		}
	}

	def createEventSet(self, procText):

		eventSet = []
		if self.delimiter == "<whitespace(s)>":
			splitText = procText.split()
		else:
			splitText = procText.split(self.delimiter[0])

		for word in splitText:
			eventSet += [str(word[letterIndex] + "_" + str(letterIndex)) for letterIndex in range(len(word))]
		return eventSet

	def setParams(self, params):
		'''This function is required, but does not do anything for this event driver.'''
		pass
	
	def displayName():
		return "Character Position"

	def displayDescription():
		return "Converts delimited words into list of letters with their positions within the word.\nRecommended with the Cangjie canonicizer"


class WithinWordNGram(EventDriver):
	n = 2
	delimiter = "<whitespace(s)>"
	_variable_options = {
		"delimiter":
		{
			"options": ["<whitespace(s)>", ", (comma)", ". (period)", "; (semicolon)"],
			"type": "OptionMenu",
			"default": 0
		},
		"n":
		{
			"options": list(range(4)),
			"type": "OptionMenu",
			"default": 0
		}
	}
	
	def displayName():
		return "Within-word n-gram [under construction]"

	def displayDescription():
		return "Lists the n-gram of letter sequences within a word."



	def createEventSet(self, procText):

		eventSet = []
		if self.delimiter == "<whitespace(s)>":
			splitText = procText.split()
		else:
			splitText = procText.split(self.delimiter[0])

		for word in splitText:
			eventSet += [str(word[letterIndex] + "_" + str(letterIndex)) for letterIndex in range(len(word))]
		return eventSet
	
class SpacyLemmatize(EventDriver):
# class var.
	_SpacyLemmatize_module_dict = {
		"English": "en_core_web_sm",
		"Chinese (GB2123)": "zh_core_web_sm",
		"Japanese": "ja_core_news_sm",
		# see https://spacy.io/usage/models
		# for language module names.
	}
	# class var.
	_SpacyLemmatize_lang_pipeline = None

		
	def displayName():
		return "Lemmatize (Spacy)"

	def displayDescription():
		return "Lemmatize words using the Spacy module."
	
		
	def setParams(self, params):
		'''Accepts a list of parameters and assigns them to the appropriate variables.'''

	
	def createEventSet(self, procText):
		"""Lemmatize using spacy"""

		if EventDriver._spacy_lang_pipeline == None:
			EventDriver._spacy_lang_pipeline = spacy.load(
				self._SpacyLemmatize_module_dict.get(
					self._global_parameters["language"],
					"xx_ent_wiki_sm"
				)
			)
		lem = [
			token.lemma_ for
			token in
			EventDriver._spacy_lang_pipeline(procText)
		]
		#print(lem)
		return lem
