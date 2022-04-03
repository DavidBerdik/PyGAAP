#!/usr/bin/env python3
import sys

from backend.CLI import cliMain
from Constants import version

def main():
	if len(sys.argv) >= 2:	
		print("PyGAAP v" + version + "\nby David Berdik")
		cliMain()
	else:
		import backend.GUI

if __name__=="__main__":
	main()