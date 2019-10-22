#!/usr/bin/env python3
import logging.config

def main():
	# Set logging configuration
	logging.config.fileConfig('PyGAAPLogging.config')
	logger = logging.getLogger(__name__)
	
	# TODO: A GUI-based version of PyGAAP. For now, it's all CLI.
	logger.info("Testing PyGAAP logging")

if __name__=="__main__":
	main()