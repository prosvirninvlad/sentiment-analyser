import lxml.html as html
import feedback
import math
import re

from curl.curl import Curl

class FeedbacksType:
    NEGATIVE = 0
    POSITIVE = 1

class DeliveryFeedbackParser:
    def __init__(self):
        pass

    def receiveFeedbacks(self, restaurantId, feedbacksType = FeedbacksType.POSITIVE):
        pagesAmount = self.countFeedbacksPages(restaurantId, feedbacksType)
        return self.parseFeedbacksPages(restaurantId, feedbacksType, pagesAmount)

    def countFeedbacksPages(self, restaurantId, feedbacksType):
        mainPageTree = self.receivePageTree(restaurantId, feedbacksType)
        if mainPageTree is not None:
            contentSection = mainPageTree.get_element_by_id("content")
            feedbacksPages = contentSection.xpath("div[last()]/div/h1/span/text()").pop()
            feedbacksPages = int(re.findall(r"(\d+)", feedbacksPages).pop())
            return math.ceil(feedbacksPages / 20)
        else:
            return 0

    def parseFeedbacksPages(self, restaurantId, feedbacksType, pagesAmount):
        feedbacks = []
        for pageId in range(1, pagesAmount + 1):
            pageTree = self.receivePageTree(restaurantId, feedbacksType, pageId)
            if pageTree is not None: feedbacks.extend(self.deriveFeedbacks(pageTree))
        return feedbacks

    def receivePageTree(self, restaurantId, feedbacksType, pageId = 1):
        restaurantUrl = self.prepareRestaurantUrl(restaurantId, feedbacksType, pageId)
        pageContent = Curl().sendGetRequest(restaurantUrl)
        return html.fromstring(pageContent) if pageContent else None

    def prepareRestaurantUrl(self, restaurantId, feedbacksType, pageId):
        restaurantUrl = "http://www.delivery-club.ru/srv/{}/feedbacks/{}/page/{}"
        feedbacksType = "positive" if feedbacksType == FeedbacksType.POSITIVE else "negative"
        return restaurantUrl.format(restaurantId, feedbacksType, pageId)

    def deriveFeedbacks(self, pageTree):
        feedbacksList = pageTree.find_class("feedbacks_list").pop()
        return [self.parseFeedbackElement(feedback) for feedback in feedbacksList.xpath("li")]

    def parseFeedbackElement(self, element):
        value = element.classes.pop() == "plus"
        content = element.xpath("div/p").pop().text
        return feedback.Feedback(content.strip(), value)