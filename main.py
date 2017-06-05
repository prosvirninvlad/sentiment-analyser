#! /usr/bin/env python3
import sys

from delivery.parser import FeedbacksType
from delivery.search import DeliverySearch
from delivery.classifier import Classifier
from delivery.parser import DeliveryFeedbackParser

def main(args):
    if args: parseArgs(args)
    else: help()

def parseArgs(args):
    option = args[0]
    if option == "--train": train()
    elif option == "--benchmark": benchmark()
    elif option == "--collect": parseCollectArgs(args[1:])
    elif option == "--classify": classify(args[1:])
    else: help()

def parseCollectArgs(args):
    try:
        restaurantName = args[0]
        benchmark = args[5] if len(args) > 5 else ""
        number = int(args[4]) if len(args) > 4 else 0
        benchmark = True if benchmark == "--benchmark" else False
        feedbacksType =  FeedbacksType.NEGATIVE if args[2] == "neg" else FeedbacksType.POSITIVE
        collect(restaurantName, feedbacksType, benchmark, number)
    except IndexError: help()

def train():
    classifier = Classifier.instance()
    classifier.train()

def collect(restaurantName, feedbacksType, benchmark = False, howMany = 0):
    search = DeliverySearch()
    parser = DeliveryFeedbackParser()
    classifier = Classifier.instance()
    for pos, restaurant in enumerate(search.searchRestaurant(restaurantName)):
        print("({}) Parsing {}.".format(pos, restaurant.name))
        for feedback in parser.receiveFeedbacks(restaurant.id, feedbacksType, howMany):
            feedback.test = benchmark
            classifier.appendFeedback(feedback)

def benchmark():
    classifier = Classifier().instance()
    print("Accuracy: {:.2f}%".format(classifier.benchmark() * 100))

def classify(args):
    classifier = Classifier.instance()
    negChance, posChance = classifier.classify(args.pop())
    classifierResult = posChance > negChance
    print("Результат: {}".format("+" if classifierResult else "-"))

def help():
    print("Usage: [--collect restaurant_name --type pos|neg --how-many number [--benchmark]] [--train] [--benchmark] [--classify content]")

if __name__ == "__main__":
    if sys.argv: main(sys.argv[1:])