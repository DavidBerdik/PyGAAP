from abc import ABC, abstractmethod
import backend.Histograms as histograms
from gensim import corpora
from gensim.summarization import bm25
import jieba.posseg as pseg

# An abstract AnalysisDriver class.
class AnalysisDriver(ABC):
	distance = None
	
	@abstractmethod
	def train(self, knownDocuments):
		'''Train a model on the knownDocuments.'''
		pass
		
	@abstractmethod
	def analyze(self, unknownDocument):
		'''Analyze unknownDocument'''
		pass

	@abstractmethod
	def displayName():
		'''Returns the display name for the given analysis method.'''
		pass
		
	def setDistanceFunction(self, distance):
		'''Sets the distance function to be used by the analysis driver.'''
		self.distance = distance
		
class CentroidDriver(AnalysisDriver):
	authorHistograms = None
	
	def train(self, knownDocuments):
		'''Get a mean normalized histogram for each known author.'''
		self.authorHistograms = histograms.generateKnownDocsMeanHistograms(histograms.generateKnownDocsNormalizedHistogramSet(knownDocuments))
		
	def analyze(self, unknownDocument):
		'''Compare a normalized histogram of unknownDocument against the normalized known document histograms and return a dictionary of distances.'''
		results = dict()
		for author, knownHist in self.authorHistograms.items():
			results[author] = self.distance.distance(histograms.normalizeHistogram(histograms.generateAbsoluteHistogram(unknownDocument)), knownHist)
		return results
	
	def displayName():
		return "Centroid Driver"
		
class BM25DriverChinese(AnalysisDriver):
	query = []
	dictionary = []
	average_idf = 0.0
	def tokenization(filename):
		'''Remove characters or words with these kinds of part of speech'''
		stop_flag = ['x', 'c', 'u','d', 'p', 't', 'uj', 'm', 'f', 'r']
		result = []
		text = open(filename,"rb").read()
		words = pseg.cut(text)
		for word, flag in words:
			if flag not in stop_flag:
				result.append(word)
		return result

	def train(self, knownDocuments):
		for root,dirs,files in os.walk(dirname):
			for f in knownDocuments:
				corpus.append(tokenization(f))
				filenames.append(f)
		dictionary = corpora.Dictionary(corpus)
		doc_vectors = [dictionary.doc2bow(text) for text in corpus]
		vec1 = doc_vectors[0]

		bm25Model = bm25.BM25(corpus)
		average_idf = sum(map(lambda k: float(bm25Model.idf[k]), bm25Model.idf.keys())) / len(bm25Model.idf.keys())

	def analyze(self, unknownDocument):
		url_k_words = "articles/sanchongmen_ch5.txt"
		sentence = open(url_k_words,"rb").read()
		# Based on TF-IDF to get key words
		# tags = jieba.analyse.extract_tags(sentence, withWeight=True, topK=20, allowPOS=())
		# Based on TextRank to get top K words
		tags =jieba.analyse.textrank(sentence, topK=20, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v'))
		query = tags
		scores = bm25Model.get_scores(query)
		# scores.sort(reverse=True)
		idx = scores.index(max(scores))
		fname = filenames[idx]
		return fname
	def displayName():
		return "BM25 Driver for Chinese"