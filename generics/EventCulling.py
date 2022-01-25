from abc import ABC, abstractmethod

# An abstract Event Culling class.
class EventCulling(ABC):
	@abstractmethod
	def process(self, procText):
		'''To be determined'''
		pass
		
	@abstractmethod
	def displayName():
		'''Returns the display name for the given event culler.'''
		pass

	@abstractmethod
	def displayDescription():
		'''Returns the display description for the event culler.'''
		
class EmptyEventCuller(EventCulling):
	test_param1=2
	test_param2=14
	_variable_options={"test_param1": list(range(2, 8)), "test_param2": list(range(10, 15))} # for PyGAAP GUI to know which options to list/are valid
	_variable_GUItype={"test_param1": "OptionMenu", "test_param2": "OptionMenu"}		# for PyGAAP GUI to know what kind of tkinter widget to use to set the variables. Can be "OptionMenu" or "Entry"
	
	def process(self, procText):
		pass

	def displayName():
		return "Test event culler"

	def displayDescription():
		return "An empty event culler class."