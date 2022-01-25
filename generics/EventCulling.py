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
		
class NormalizeWhitespace(EventCulling):
	def process(self, procText):
		pass

	def displayName():
		return "Test event culler"

	def displayDescription():
		return "An empty event culler class."