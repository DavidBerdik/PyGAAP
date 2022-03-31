#!/usr/bin/env python3
import sys

from backend.CLI import cliMain

def main():
	if len(sys.argv) >= 2:	
		print("PyGAAP v1.0.0 alpha 1\nby David Berdik")
		cliMain()
	else:
		import backend.GUI

if __name__=="__main__":
	main()