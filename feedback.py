import collections

class Feedback:
	def __init__(self, content, value, test):
		self._content = content
		self._value = value
		self._test = bool(test)
	
	@property
	def content(self):
		return self._content
	
	@property
	def value(self):
		return self._value
	
	@property
	def test(self):
		return self._test
	
	@content.setter
	def content(self, value):
		self._content = value
	
	@value.setter
	def value(self, value):
		self._value = value
	
	@test.setter
	def test(self, value):
		self._test = bool(value)