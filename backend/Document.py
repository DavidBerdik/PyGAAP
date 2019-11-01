class Document:
	'''Document object'''
	author = ""
	title = ""
	text = ""
	eventSet = None
	filepath = ""
	
	def __init__(self, author, title, text, filepath):
		'''Document object constructor.'''
		self.author = author
		self.title = title
		self.text = text
		self.filepath = filepath
		
	def setEventSet(self, eventSet):
		'''Sets the eventSet list value.'''
		self.eventSet = eventSet