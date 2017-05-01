import re
import pymorphy2

class Lingua:
	_instance = None
	@staticmethod
	def instance():
		if Lingua._instance is None:
			Lingua._instance = Lingua.__Lingua()
		return Lingua._instance

	class __Lingua:
		def __init__(self):
			self._morphy = pymorphy2.MorphAnalyzer()
			self._unigram_regex = re.compile(r"([а-яА-Яa-zA-Z]+)")

		def vectorize(self, content):
			return self._genUnigrams(content)
		
		def process(self, content):
			for sentence in self._genSentences(content):
				print(sentence)
				for unigram in self._genUnigrams(sentence):

					print("{}: {}".format(unigram, ", ".join(p.tag.POS for p in self._morphy.parse(unigram))))
				print("-" * 80)
		
		def _normalize(self):
			pass
		
		def _genSentences(self, content):
			yield from re.split("[?!.]", content)

		def _genUnigrams(self, content):
			for unigram in self._unigram_regex.findall(content):
				if len(unigram) > 1: yield unigram.lower()

if __name__ == "__main__":
	content = """Все было очень вкусно. Прекрасные роллы с кучей рыбы. Мидии пробовал в 
	первый раз, вкуснота. единственный минус - дороговато, но еда понравилось. если захочу 
	сушей - обязательно возьму там же.
	"""
	lingua = Lingua.instance()
	lingua.process(content)