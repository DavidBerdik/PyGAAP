class Document:
	'''Document object'''
	author = ""
	title = ""
	text = ""
	eventSet = None
	
	def __init__(self, author, title, text):
		self.author = author
		self.title = title
		self.text = text