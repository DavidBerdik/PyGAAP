from generics.Canonicizer import Canonicizer

class NormalizeWhitespace(Canonicizer):
	def process(self, procText):
		'''Convert procText in to a character list where all whitespace characters are the same.'''
		return list(' '.join(procText.split()))

	def displayName(self):
		return "Normalize Whitespace"