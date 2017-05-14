import math
from functools import reduce

from lingua import Word
from lingua import Lingua
from dao.database import Database

class Classifier:
    _instance = None
    @staticmethod
    def instance():
        if Classifier._instance is None:
            Classifier._instance = Classifier.__Classifier()
        return Classifier._instance
    
    class __Classifier:
        def __init__(self):
            self.patterns = (
                # Существительное и прилагательное
                (Word.NOUN, Word.ADJF),
                (Word.ADJF, Word.NOUN),
                # Наречие и наречие
                (Word.ADVB, Word.ADVB),
                # Существительное и наречие
                (Word.ADJF, Word.ADVB),
                (Word.ADVB, Word.ADJF),
                # Глагол и наречие
                (Word.ADVB, Word.VERB),
                (Word.VERB, Word.ADVB),
                # Прилагательное и прилагательное
                (Word.ADJF, Word.ADJF),
                # Глагол и прилагательное
                (Word.VERB, Word.ADJF),
                (Word.ADJF, Word.VERB),
            )
            self._lingua = Lingua.instance()
            self._database = Database.instance()
            self._unigramsByClass = self._database.countUnigrams()
            self._uniqueUnigrams = self._database.countUniqueUnigrams()
            self._feedbacks = sum(self._database.countFeedbacksByClass(value) for value in range(2))
        
        def appendFeedback(self, feedback):
            self._database.insertFeedback(feedback)
        
        def benchmark(self):
            truePos = trueNeg = falsePos = falseNeg = 0
            for num, feedback in enumerate(self._database.selectFeedbacks(True)):
                expertValue = bool(feedback.value)
                classifierValue = self.classify(feedback.content)
                print("({}): {}/{}".format(num, expertValue, classifierValue))
                if expertValue:
                    if classifierValue: truePos += 1
                    else: falseNeg += 1
                else:
                    if classifierValue: falsePos += 1
                    else: trueNeg += 1
            accuracy = (truePos + trueNeg) / (truePos + trueNeg + falsePos + falseNeg)
            posPrecision = truePos / (truePos + falsePos)
            print("posPrecision: {:.2f}%".format(posPrecision * 100))
            negPrecision = trueNeg / (trueNeg + falseNeg)
            print("negPrecision: {:.2f}%".format(negPrecision * 100))
            posRecall = truePos / (truePos + falseNeg)
            print("posRecall: {:.2f}%".format(posRecall * 100))
            negRecall = trueNeg / (trueNeg + falsePos)
            print("negRecall: {:.2f}%".format(negRecall * 100))
            return accuracy

        def train(self):
            bigrams = dict()
            unigrams = dict()
            for feedback in self._database.selectFeedbacks():
                for bigram in filter(lambda x: self._lingua.matchMorphyPatterns(
                    x, self.patterns), self._lingua.vectorize(feedback.content)
                ):
                    bigrams.setdefault(bigram, [1, 1])[feedback.value] += 1
                    for unigram in bigram:
                        unigrams.setdefault(unigram, [1, 1])[feedback.value] += 1
            
            bigramsSum = [sum(bigrams[key][i] for key in bigrams) for i in range(2)]
            unigramsSum = [sum(unigrams[key][i] for key in unigrams) for i in range(2)]
            ngramsSum = [bigramsSum[i] + unigramsSum[i] for i in range(2)]

            result = dict()
            for bigram in bigrams:
                measure = 0
                for i in range(2):
                    bigramFrequency = bigrams[bigram][i] / bigramsSum[i]
                    unigramsFrequency = [unigrams[unigram][i] / unigramsSum[i] for unigram in bigram]
                    unigramsFrequency = reduce(lambda res, x: res * x, unigramsFrequency, 1.)
                    measure += math.log(bigramFrequency * ngramsSum[i] / unigramsFrequency, 2)
                measure /= 2.
                if measure > 16:
                    result[self._lingua.concatenateUnigrams(bigram)] = bigrams[bigram]

            self._database.deleteUnigrams()
            self._database.insertUnigrams(result)

        def classify(self, content):
            result = [0, 0]
            unigrams = filter(lambda x: self._lingua.matchMorphyPatterns(
                x, self.patterns), self._lingua.vectorize(content))
            unigrams = tuple(self._lingua.concatenateUnigrams(bigram) for bigram in unigrams)
            # print(content)
            # print(unigrams)
            # input()
            for value in range(2):
                logDenom = self._uniqueUnigrams + self._unigramsByClass[value]
                result[value] = math.log(self._unigramsByClass[value] / self._feedbacks) + sum(math.log((
                    self._database.selectUnigramUsage(unigram, value) + 1) / logDenom
                ) for unigram in unigrams)
            return result[0] < result[1]