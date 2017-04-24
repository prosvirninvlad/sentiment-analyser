import re
import math

from dao.database import Database

class Classifier:
    def __init__(self):
        self._unigrams = dict()
        self._feedbacks = list()
        self._database = Database.instance()
        self._unigram_regex = re.compile(r"([а-яА-Яa-zA-Z]+)")

    def learn(self, feedback):
        self._feedbacks.append(feedback)
        unigrams = self._deriveUnigrams(feedback.content)
        for unigram in unigrams:
            self._unigrams.setdefault(unigram, [0, 0])[feedback.value] += 1

    def close(self):
        self._database.insertUnigrams(self._unigrams)
        self._database.insertFeedbacks(self._feedbacks)

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
        return result

    def _deriveUnigrams(self, content):
        return [unigram.lower() for unigram in self._unigram_regex.findall(content) if len(unigram) > 1]