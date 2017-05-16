import math
import sqlite3
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
                classifierValue, percentages = self.classify(feedback.content)
                print("({}): {}/{} (+: {:.2f}%, -: {:.2f}%)".format(num, expertValue, classifierValue, *percentages))
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
            # self.collectBigrams()
            self.removeUselessBigrams()
        
        def collectBigrams(self):
            bigrams = dict()
            for feedback in self._database.selectFeedbacks():
                for unigramA, unigramB in self._lingua.vectorize(feedback.content):
                    bigrams.setdefault(unigramA, dict())
                    bigrams[unigramA].setdefault(unigramB, [0, 0])
                    bigrams[unigramA][unigramB][feedback.value] += 1
            self._database.deleteBigrams()
            self._database.insertBigrams(bigrams)

        def removeUselessBigrams(self):
            self._database.deleteUnigrams()
            pos, neg = self._database.countBigrams()
            for bigram in self._database.selectBigrams():
                success = True
                unigramA, unigramB, *repeats = bigram
                for value in range(2):
                    XY, XNY, NXY, NXNY = [usage / pos for usage in self._database.countBigramUsage((unigramA, unigramB), value)]
                    success &= math.log(XY / ((XY + XNY) * (XY + NXY) / (XY + XNY + NXY + NXNY)), 2) > 3
                if success:
                    self._database.insertUnigram(("{} {}".format(unigramA, unigramB), *repeats))

        def classify(self, content):
            result = [0, 0]
            unigrams = self._lingua.vectorize(content)
            unigrams = tuple(self._lingua.concatenateUnigrams(bigram) for bigram in unigrams)
            for value in range(2):
                logDenom = self._uniqueUnigrams + self._unigramsByClass[value]
                result[value] = math.log(self._unigramsByClass[value] / self._feedbacks) + sum(math.log((
                    self._database.selectUnigramUsage(unigram, value) + 1) / logDenom
                ) for unigram in unigrams)
            exps = [math.exp(val) for val in result]
            exps = [exp / (sum(exps) + 0.01) * 100 for exp in exps]
            # print(content)
            # print(unigrams)
            # input()
            return result[0] < result[1], exps