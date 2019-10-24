import csv

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