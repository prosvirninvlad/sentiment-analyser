import re
import pymorphy2

class Word:
	NOUN = "NOUN"
	ADJF = "ADJF"
	ADJS = "ADJS"
	COMP = "COMP"
	VERB = "VERB"
	INFN = "INFN"
	PRTF = "PRTF"
	PRTS = "PRTS"
	GRND = "GRND"
	NUMR = "NUMR"
	ADVB = "ADVB"
	NPRO = "NPRO"
	PRED = "PRED"
	PREP = "PREP"
	CONJ = "CONJ"
	PRCL = "PRCL"
	INTJ = "INTJ"

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
			self._unigram_regex = re.compile(r"([а-яёЁА-Яa-zA-Z]+|[,;])")

		def vectorize(self, content):
			return self._genUnigrams(content)
			# return self.analyse(content)
			bigram = ""
			unigrams = []
			append = False
			for unigram in self._genUnigrams(content):
				# unigram = self._morphy.parse(unigram).pop()
				# unigram = unigram.normal_form
				if append:
					unigrams.append("{} {}".format(bigram, unigram))
				bigram = unigram
				append = not append
			return unigrams

		def analyse(self, content):
			sentences = self._genSentences(content)
			for sentence in sentences: self._analyseSentence(sentence)
		
		def _analyseSentence(self, sentence):
			noun = adjv = ""
			for p in sentence.split(","):
				unigrams = tuple(self._genUnigrams(p))
				for x in range(len(unigrams)):
					for y in range(x + 1, len(unigrams)):
						unigramA = unigrams[x]
						unigramB = unigrams[y]
						namingA = self._getWordNaming(unigramA)
						namingB = self._getWordNaming(unigramB)
						sign = namingA == Word.ADJF and namingB == Word.NOUN
						sign = namingA == Word.NOUN and namingB == Word.ADJF or sign
						if (sign): print("{} {}".format(unigramA, unigramB))
		
		def _getWordNaming(self, word):
			parsed = self._morphy.parse(word)
			voting = dict()
			for parse in parsed:
				parse = parse.tag.POS
				voting.setdefault(parse, 0)
				voting[parse] += 1
			naming = max(voting, key = lambda x: voting[x])
			return self._normalizeWordNaming(naming)
		
		def _normalizeWordNaming(self, naming):
			if naming == Word.ADJS: naming = Word.ADJF
			elif naming == Word.INFN: naming = Word.VERB
			elif naming == Word.PRTS: naming = Word.PRTF
			return naming
		
		def _genSentences(self, content):
			yield from re.split("[?!.]", content)

		def _genUnigrams(self, content):
			for unigram in self._unigram_regex.findall(content):
				if len(unigram) > 1: yield unigram.lower()

if __name__ == "__main__":
	contents = [
		"Еда была теплая, читал отзывы, боялся, что будет холоднее, но по мне все отлично! Бургеры с закуской были восхитительные, с радостью буду заказывать у вас снова :)",
		"Заказ привезли в оговоренный срок. Еда вкусная, не остывшая",
		"Бургер был вкусный, реально, все остальное так себе"
	]
	lingua = Lingua.instance()
	for content in contents:
		lingua.analyse(content)