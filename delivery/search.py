import re
import json

from curl.curl import Curl
from delivery.restaurant import Restaurant

class DeliverySearch:
    def __init__(self):
        pass

    def searchRestaurant(self, name):
        apiUrl = self.prepareApiUrl(name)
        return self.sendSearchApiRequest(apiUrl)

    def prepareApiUrl(self, name):
        apiUrl = "http://www.delivery-club.ru/ajax/quick_search/?cid=1&q={}&mode=food"
        name = name.replace(" ", "+")
        return apiUrl.format(name)

    def sendSearchApiRequest(self, url):
        curlHandler = Curl()
        response = curlHandler.sendGetRequest(url)
        return self.parseApiResponse(response) if response else []

    def parseApiResponse(self, response):
        decoder = json.JSONDecoder()
        restaurants = decoder.decode(response)
        return [self.parseJsonElement(restaurant) for restaurant in restaurants]

    def parseJsonElement(self, element):
        name = element.get("title", "")
        name = re.sub(r"<[^>]*>", "", name)
        return Restaurant(
            element.get("title_en", ""),
            name
        )
