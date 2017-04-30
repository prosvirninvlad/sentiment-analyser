import re
import math

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
            self._database = Database.instance()
            self._unigram_regex = re.compile(r"([а-яА-Яa-zA-Z]+)")
        
        def appendFeedback(self, feedback):
            self._database.insertFeedback(feedback)
        
        def benchmark(self):
            truePos = trueNeg = falsePos = falseNeg = 0
            for feedback in self._database.selectFeedbacks(True):
                expertValue = feedback.value
                classifierValue = self.classify(feedback.content)
                if expertValue:
                    if classifierValue: truePos += 1
                    else: falsePos += 1
                else:
                    if classifierValue: falseNeg += 1
                    else: trueNeg += 1
            return (truePos + trueNeg) / (truePos + trueNeg + falsePos + falseNeg)

        def train(self):
            unigrams = dict()
            for feedback in self._database.selectFeedbacks():
                for unigram in self._deriveUnigrams(feedback.content):
                    unigrams.setdefault(unigram, [0, 0])[feedback.value] += 1
            self._database.deleteUnigrams()
            self._database.insertUnigrams(unigrams)

        def classify(self, content):
            unigrams = self._deriveUnigrams(content)
            unigramsByClass = self._database.countUnigrams()
            uniqueUnigrams = self._database.countUniqueUnigrams()
            feedbacks = sum(
                self._database.countFeedbacksByClass(value) for value in range(2)
            )
            result = [0, 0]
            for value in range(2):
                logDenom = uniqueUnigrams + unigramsByClass[value]
                result[value] = math.log(unigramsByClass[value] / feedbacks) + sum(math.log((
                    self._database.selectUnigramUsage(unigram, value) + 1) / logDenom
                ) for unigram in unigrams)
            return result[0] < result[1]

        def _deriveUnigrams(self, content):
            return [unigram.lower() for unigram in self._unigram_regex.findall(content) if len(unigram) > 1]