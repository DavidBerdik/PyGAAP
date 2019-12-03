from abc import ABC, abstractmethod
import jieba


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
		
class WordSegmentationForChinese(Canonicizer):
	def process(self, procText):
		
		'''
		# different cut modes
		segfull_list = jieba.cut("content here", cut_all=True) #Full mode
		segdef_list = jieba.cut(""content here"", cut_all=False) #Default Mode
		seg_search_list = jieba.cut_for_search(""content here"")  # search mode
		'''
		#content = open(procText,"rb").read()
		words = " ".join(jieba.cut(procText, cut_all=False)) #Default Mode
		#log_f = open(outputText,"wb")
		#log_f.write(words.encode('utf-8'))
		return words
	def displayName():
		return "Word Segmentation For Chinese"
		
class TokenizationChinese(Canonicizer)
	def process(self, procText):
		'''Remove characters or words with these kinds of part of speech'''
		stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']
		result = []
		#filename = procText
		#text = open(procText,"rb").read()
		words = pseg.cut(procText)
		for word, flag in words:
			if flag not in stop_flag:
				result.append(word)
		return result
	def displayName():
		return "Tokenization For Chinese"