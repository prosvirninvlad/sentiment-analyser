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
    elif option == "--collect": parseCollectArgs(args[1:])
    elif option == "--classify": classify(args[1:])
    else: help()

def parseCollectArgs(args):
    try:
        restaurantName = args[0]
        feedbacksType =  FeedbacksType.NEGATIVE if args[2] == "neg" else FeedbacksType.POSITIVE
        collect(restaurantName, feedbacksType)
    except IndexError: help()

def train():
    classifier = Classifier.instance()
    classifier.train()

def collect(restaurantName, feedbacksType):
    search = DeliverySearch()
    parser = DeliveryFeedbackParser()
    classifier = Classifier.instance()
    for pos, restaurant in enumerate(search.searchRestaurant(restaurantName)):
        print("({}) Parsing {}.".format(pos, restaurant.name))
        for feedback in parser.receiveFeedbacks(restaurant.id, feedbacksType):
            classifier.appendFeedback(feedback)

def classify(args):
    classifier = Classifier.instance()
    negChance, posChance = classifier.classify(args.pop())
    print("Результат: {}".format("-" if negChance > posChance else "+"))

def help():
    print("Usage: [--collect restaurant_name --type pos|neg] [--train] [--classify content]")

if __name__ == "__main__":
    if sys.argv: main(sys.argv[1:])