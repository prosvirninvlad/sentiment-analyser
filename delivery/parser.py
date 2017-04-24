import lxml.html as html
import feedback
import math

from curl.curl import Curl

class DeliveryFeedbackParser:
    def __init__(self):
        pass

    def receiveFeedbacks(self, restaurantId):
        pagesAmount = self.countFeedbacksPages(restaurantId)
        return self.parseFeedbacksPages(restaurantId, pagesAmount)

    def parseFeedbacksPages(self, restaurantId, pagesAmount):
        feedbacks = []
        for pageId in range(1, pagesAmount + 1):
            pageTree = self.receivePageTree(restaurantId, pageId)
            if pageTree is not None: feedbacks.extend(self.deriveFeedbacks(pageTree))
        return feedbacks

    def countFeedbacksPages(self, restaurantId):
        mainPageTree = self.receivePageTree(restaurantId)
        if mainPageTree is not None:
            pageTabs = mainPageTree.find_class("tabs").pop()
            feedbacksPages = pageTabs.find_class("active").pop()
            feedbacksPages = int(feedbacksPages.xpath("a/span/text()").pop())
            return math.ceil(feedbacksPages / 20)
        else:
            return 0

    def receivePageTree(self, restaurantId, pageId = 1):
        restaurantUrl = self.prepareRestaurantUrl(restaurantId, pageId)
        pageContent = Curl().sendGetRequest(restaurantUrl)
        return html.fromstring(pageContent) if pageContent else None

    def prepareRestaurantUrl(self, restaurantId, pageId):
        restaurantUrl = "http://www.delivery-club.ru/srv/{}/feedbacks/page/{}"
        return restaurantUrl.format(restaurantId, pageId)

    def deriveFeedbacks(self, pageTree):
        feedbacksList = pageTree.find_class("feedbacks_list").pop()
        return [self.parseFeedbackElement(feedback) for feedback in feedbacksList.xpath("li")]

    def parseFeedbackElement(self, element):
        value = element.classes.pop() == "plus"
        content = element.xpath("div/p").pop().text
        return feedback.Feedback(content.strip(), value)