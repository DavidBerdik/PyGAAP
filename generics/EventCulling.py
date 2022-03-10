from abc import ABC, abstractmethod
from importlib import import_module

external_modules = {}
# external imports must use "backend.import_external"
for mod in external_modules:
	external_modules[mod] = import_module(mod)



# An abstract Event Culling class.
class EventCulling(ABC):

	def __init__(self):
		try:
			for variable in self._variable_options:
				setattr(self, variable, self._variable_options[variable]["options"][self._variable_options[variable]["default"]])
		except:
			self._variable_options = dict()

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
	test_param3="op1"
	_variable_options={"test_param1": {"options": list(range(2, 8)), "default": 0, "type": "OptionMenu"},
					   "test_param2": {"options": list(range(10, 15)), "default": 4, "type": "OptionMenu"},
					   "test_param3": {"options": ["op1", "op2"], "default": 0, "type": "OptionMenu"}}
	
	def process(self, procText):
		pass

	def displayName():
		return "Test event culler"

	def displayDescription():
		return "An empty event culler class."