import argparse, os, sys

from backend.API import API
from backend.CSVIO import *
from backend.Document import Document
from pathlib import Path
from time import time

gui = False

def cliMain():
	'''Main function for the PyGAAP CLI'''
	args = _parse_args()
	
	# If a CSV file has been specified, process it.
	if args.experimentengine:
		# Get a list of experiments in the CSV.
		expCsvPath = args.experimentengine[0]
		experiments = readExperimentCSV(expCsvPath)
		
		# Process each experiment entry in the CSV.
		for exp in experiments:
			# Get a list of entries in the specified corpus CSV.
			corpusEntries = readCorpusCSV(findCorpusCSVPath(exp[-1]))
			
			# Build a list of Documents using the entries in corpusEntries.
			docs = []
			for entry in corpusEntries:
				docs.append(Document(entry[0], entry[2], readDocument(entry[1]), entry[1]))
				
			# Extract specified canonicizers, event drivers, analysis methods, and distance functions
			canonicizers = exp[1].split('&') # More than one canonicizer can be separated in a &-delimited list.
			eventDriver = exp[2]
			analysisMethod = exp[3]
			distanceFunc = exp[4]
			
			# Create the API object that will be used to actually run the experiment.
			api = API(docs)
			
			# Run each specified canonicizer against the documents in the API object.
			for canonicizer in canonicizers:
				api.runCanonicizer(canonicizer)
			
			# Run the event driver against the documents in the API object.
			api.runEventDriver(eventDriver)
			
			# Run the analysis and get the results in a formatted string.
			unknownDoc, results = api.runAnalysis(analysisMethod, distanceFunc)
			formattedResults = api.prettyFormatResults(canonicizers, eventDriver, analysisMethod, distanceFunc, unknownDoc, results)
			
			# Create the directories that the results will be stored in.
			outPath = os.path.join(Path.cwd(), "tmp", '&'.join(canonicizers).replace('|', '_').replace(':', '_'), eventDriver.replace('|', '_').replace(':', '_'), analysisMethod + '-' + distanceFunc)
			if not os.path.exists(outPath):
				os.makedirs(outPath)
			expFile=open(os.path.join(outPath,str(int(time())) + ".txt"), 'w')
			expFile.write(formattedResults)
			expFile.close()

def _parse_args(empty=False):
	"""Parse command line arguments"""
	parser = argparse.ArgumentParser(description='Welcome to PyGAAP\u2014the Python Graphical Authorship Attribution Program')
	parser.add_argument('-ee', '--experimentengine', metavar='csv-file', nargs=1, help="Specifies a CSV file for batch processing multiple experiments at once.")
	# If no arguments specified, print help and completely exit.
	if empty:
		parser.print_help()
		sys.exit(1)
	
	# Return parsed arguments.
	return parser.parse_args()