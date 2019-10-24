class Document:
	'''Document object'''
	author = ""
	title = ""
	text = ""
	eventSet = None
	
	def __init__(self, author, title, text):
		'''Document object constructor.'''
		self.author = author
		self.title = title
		self.text = text
		
	def setEventSet(self, eventSet):
		'''Sets the eventSet list value.'''
		self.eventSet = eventSet