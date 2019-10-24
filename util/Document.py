class Document:
	author = ""
	filepath = ""
	title = ""
	text = ""
	
	def __init__(self, author, filepath, title, text):
		self.author = author
		self.filepath = filepath
		self.title = title
		self.text = text