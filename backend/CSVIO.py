import csv, pathlib

def readCorpusCSV(csvPath):
	'''Read the corpus csv at the given path in to a list of lists and return it.'''
	# Read each row from the CSV in to a list.
	csvRows = []
	with open(csvPath) as file:
		readCSV = csv.reader(file, delimiter=',')
		for row in readCSV:
			csvRows.append(row)
	return csvRows
	
def readExperimentCSV(csvPath):
	'''Read the experiment CSV at the given path in to a list of lists and return it.'''
	csvRows = readCorpusCSV(csvPath) # Reading is the same for the corpus CSV except for the experiment CSV we delete the last line.
	# Remove the header entry from the list and return it.
	del csvRows[0]
	return csvRows
	
def findCorpusCSVPath(corpusCSVPathEntry):
	'''Find the corpus CSV's path based on the experiment CSV's path entry.'''
	return pathlib.Path(corpusCSVPathEntry).absolute()
	
def findDocumentPath(documentPathEntry):
	'''Find the path of the specified document based on the document path entry.'''
	return findCorpusCSVPath(documentPathEntry)
	
def readDocument(documentPath):
	'''Returns the contents of the document at the specified path.'''
	try:
		return pathlib.Path(documentPath).read_text()
	except UnicodeError:
		return pathlib.Path(documentPath).read_text(encoding="UTF-8")
