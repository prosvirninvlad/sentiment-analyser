import re
import Stemmer
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

BIGRAM_PATTERNS = (
	(Word.NOUN, Word.ADJF),
	(Word.ADVB, Word.ADVB),
	(Word.ADJF, Word.ADVB),
	(Word.ADVB, Word.VERB),
	(Word.ADJF, Word.ADJF),
	(Word.VERB, Word.ADJF),
)

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
			self._stemmer = Stemmer.Stemmer("russian")
			self._unigram_regex = re.compile(r"([а-яёЁА-Яa-zA-Z]+)")

		def vectorize(self, content):
			return self._genBigrams(content)
		
		def _genBigrams(self, content):
			for sentence in self._genSentences(content):
				for area in [x.strip() for x in re.split("[;,]", sentence)]:
					unigrams = self._genUnigrams(area)
					for i in range(len(unigrams) - 1):
						yield (unigrams[i], unigrams[i + 1])

		def concatenateUnigrams(self, unigrams):
			return " ".join(unigrams)
		
		def matchMorphyPatterns(self, bigram):
			namings = tuple(self._getWordNaming(unigram) for unigram in bigram)
			# print("{} {}: {} {}".format(*bigram, *namings))
			for pattern in BIGRAM_PATTERNS:
				if namings == pattern: return tuple(self._stemmer.stemWords(bigram))
				reverse = tuple(reversed(namings))
				if reverse == pattern: return tuple(self._stemmer.stemWords(reversed(bigram)))
			return None

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
			return [unigram.lower() for unigram in self._unigram_regex.findall(content) if len(unigram) > 1]