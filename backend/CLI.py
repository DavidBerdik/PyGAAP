import argparse, logging, sys

from  backend.CSVIO import readCSV

def cliMain():
	"""Main function for the PyGAAP CLI"""	
	if len(sys.argv) < 2:
		_parse_args(True)
		
	args = _parse_args()
	
	# If a CSV file has been specified, process it.
	if args.experimentengine:
		readCSV(args.experimentengine[0])

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