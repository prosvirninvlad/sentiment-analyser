import requests

class Curl:
    def __init__(self):
        pass

    def sendGetRequest(self, url):
        response = ""
        try:
            response = requests.get(url)
            response = response.text
        except requests.RequestException:
            pass
        return response