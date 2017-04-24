#! /usr/bin/env python3
import sys

from delivery.parser import DeliveryFeedbackParser
from delivery.search import DeliverySearch
from delivery.classifier import Classifier
from dao.database import Database

def train(args):
    classifier = Classifier()
    deliverySearch = DeliverySearch()
    deliveryParser = DeliveryFeedbackParser()
    restaurants = deliverySearch.searchRestaurant(args.pop())
    for pos, restaurant in enumerate(restaurants):
        print("({}) Parsing \"{}\"".format(pos, restaurant.name))
        for feedback in deliveryParser.receiveFeedbacks(restaurant.id):
            classifier.learn(feedback)
    classifier.close()

def classify(args):
    negChance, posChance = Classifier().classify(args.pop())
    print("Результат: {}".format("-" if negChance > posChance else "+"))

def main(args):
    option = args[0] if args else ""
    if option == "--train": train(args[1:])
    elif option == "--classify": classify(args)
    else: print("Usage: --train restaurant_name|--classify content")

if __name__ == "__main__":
    if sys.argv: main(sys.argv[1:])