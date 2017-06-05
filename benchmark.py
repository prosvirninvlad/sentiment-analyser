#! /usr/bin/env python3
import nltk
import lingua
import dao.database
import delivery.classifier
from nltk.classify import SklearnClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier

ln = lingua.Lingua.instance()
db = dao.database.Database.instance()
cl = delivery.classifier.Classifier.instance()

print("System is training. Please wait.")
data = [([cl.buildUnigram(y) for y in ln.vectorize(x.content) if cl.validateBigram(y)], x.value) for x in db.selectFeedbacks()]
test = [([cl.buildUnigram(y) for y in ln.vectorize(x.content) if cl.validateBigram(y)], x.value) for x in db.selectFeedbacks(test = True)]

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
      all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

word_features = get_word_features(get_words_in_tweets(data))
def extract_features(document):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

training_set = nltk.classify.apply_features(extract_features, data)
classifier = SklearnClassifier(SVC(), sparse = False).train(training_set)
# classifier = SklearnClassifier(RandomForestClassifier(), sparse = False).train(training_set)
truePos = trueNeg = falsePos = falseNeg = 1
for num, content, value in enumerate(test):
    expertValue = bool(value)
    classfValue = bool(classifier.classify(extract_features(content)))
    print("({}) Expert: {} / Classifier: {}".format(num, value, classfValue))
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
print("Accuracy: {:.2f}%".format(accuracy * 100))