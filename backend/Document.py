class Document:
	'''Document object'''
	author = ""
	title = ""
	text = ""
	eventSet = []
	filepath = ""
	
	def __init__(self, author, title, text, filepath):
		'''Document object constructor.'''
		self.author = author
		self.title = title
		self.text = text
		self.filepath = filepath
		
	def setEventSet(self, eventSet, **options):
		'''Sets the eventSet list value.'''
		append = options.get("append", False)
		if not append:
			self.eventSet = eventSet
		else:
			self.eventSet += eventSet
