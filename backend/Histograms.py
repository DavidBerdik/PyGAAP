def generateKnownDocsAbsoluteHistogramSet(documents):
	'''Generates a dictionary where author names are keys and values are lists of absolute dictionary-based histograms.'''
	# Create a dictionary of lists of documents by different authors.
	docsByAuthor = _generateAuthorDocumentDictionary(documents)
	
	# Build and return the absolute histogram.
	absHistogramsByAuthor = dict()
	for author, docs in docsByAuthor.items():
		for doc in docs:
			docEventHist = dict()
			for event in doc.eventSet:
				docEventHist[event] = docEventHist.get(event, 0) + 1
			
			try:
				absHistogramsByAuthor[author].append(docEventHist)
			except KeyError:
				absHistogramsByAuthor[author] = [docEventHist]
				
	return absHistogramsByAuthor
	
def generateKnownDocsNormalizedHistogramSet(documents):
	'''Generates a dictionary where author names are keys and values are lists of normalized dictionary-based histograms.'''
	# Start by generating absolute histograms and normalize them afterwards. This should be changed later.
	absHistogramsByAuthor = generateKnownDocsAbsoluteHistogramSet(documents)
	
	# Build and return the normalized histograms.
	normHistogramsByAuthor = dict()
	for author, hists in absHistogramsByAuthor.items():
		histList = []
		for hist in hists:
			normHist = dict()
			factor = 1.0/sum(hist.values())
			for k in hist:
				normHist[k] = hist[k]*factor
			histList.append(normHist)
		normHistogramsByAuthor[author] = histList
	
	return normHistogramsByAuthor
	
def generateKnownDocsMeanHistograms(histSet):
	'''Calculates the mean histogram for each author, given a dictionary of histograms for authors.'''
	meanHists = dict()
	
	for author, hists in histSet.items():
		# Get all keys across all histograms from the current author.
		allKeys = set()
		for hist in hists:
			allKeys.update(list(hist))
		
		# For each key, find the mean and add it to a single histogram for each author.
		meanHist = dict()
		for key in allKeys:
			avg = 0
			for hist in hists:
				avg += hist.get(key, 0)
			avg /= len(hists)
			meanHist[key] = avg
		meanHists[author] = meanHist
	return meanHists
	
def generateAbsoluteHistogram(document):
	'''Returns an absolute histogram for a given document.'''
	absHist = dict()
	for event in document.eventSet:
		absHist[event] = absHist.get(event, 0) + 1
	return absHist
	
def normalizeHistogram(histogram):
	'''Returns a normalized version of a given histogram.'''
	normHist = dict()
	factor = 1.0/sum(histogram.values())
	
	for k in histogram:
		normHist[k] = histogram[k]*factor
		
	return normHist
	
def _generateAuthorDocumentDictionary(documents):
	'''Generates a dictionary of lists of documents by author.'''
	docsByAuthor = dict()
	
	for document in documents:
		try:
			docsByAuthor[document.author].append(document)
		except KeyError:
			docsByAuthor[document.author] = [document]
			
	return docsByAuthor