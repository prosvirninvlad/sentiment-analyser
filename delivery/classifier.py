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
            self._bigramsCount = self._database.countBigrams()
            self._unigramsByClass = self._database.countUnigrams()
            self._uniqueUnigrams = self._database.countUniqueUnigrams()
            self._feedbacks = sum(self._database.countFeedbacksByClass(value) for value in range(2))
        
        def appendFeedback(self, feedback):
            self._database.insertFeedback(feedback)
        
        def benchmark(self):
            truePos = trueNeg = falsePos = falseNeg = 0
            for num, feedback in enumerate(self._database.selectFeedbacks(True)):
                expertValue = bool(feedback.value)
                negChance, posChance = self.classify(feedback.content)
                classfValue = posChance > negChance
                print("({}): {}/{} (-: {:.2f}%, +: {:.2f}%)".format(num, expertValue, classfValue, negChance, posChance))
                if expertValue:
                    if classfValue: truePos += 1
                    else: falseNeg += 1
                else:
                    if classfValue: falsePos += 1
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
            bigrams = dict()
            self._database.deleteUnigrams()
            for bigram in self._database.selectBigrams():
                unigramA, unigramB, *repeats = bigram
                unigram = (unigramA, unigramB)
                measures = self.validateBigram(unigram)
                unigram = self.buildUnigram(unigram)
                bigrams.setdefault(unigram, [0, 0])
                for pos in range(2):
                    bigrams[unigram][pos] += repeats[pos] if measures[pos] else 0
            self._database.insertUnigrams(bigrams)
        
        def buildUnigram(self, bigram):
            bigram = self._lingua.stemWords(bigram)
            return "{} {}".format(*bigram)
        
        def validateBigram(self, bigram):
            THRESHOLD = 1
            measures = []
            for value in range(2):
                XY, XNY, NXY, NXNY = [usage / self._bigramsCount[value] for usage in self._database.countBigramUsage(bigram, value)]
                measures.append(math.log(XY / ((XY + XNY) * (XY + NXY) / (XY + XNY + NXY + NXNY)), 2) >= THRESHOLD)
            return measures

        def classify(self, content):
            result = [0, 0]
            unigrams = [[], []]
            for bigram in self._lingua.vectorize(content):
                measures = self.validateBigram(bigram)
                for pos in range(2):
                    if measures[pos]: unigrams[pos].append(self.buildUnigram(bigram))
            for value in range(2):
                logDenom = self._uniqueUnigrams + self._unigramsByClass[value]
                result[value] = math.log(self._unigramsByClass[value] / self._feedbacks) + sum(math.log((
                    self._database.selectUnigramUsage(unigram, value) + 1) / logDenom
                ) for unigram in unigrams[value])
            result = [math.exp(val) for val in result]
            result = [val / sum(result) * 100 for val in result]
            return result