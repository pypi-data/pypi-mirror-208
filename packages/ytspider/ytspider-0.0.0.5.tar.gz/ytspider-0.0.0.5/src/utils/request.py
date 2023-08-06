import requests


from .context import Context

from bs4 import BeautifulSoup
class Request:
    def __init__(self):
        self.__Context = Context()
        self.__initHeaders()

    def __initHeaders(self):
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Credentials": "include"
        }

    def addHeaders(self, headers):
        self.headers.update(headers)

    def removeHeaders(self, headerNames):
        for key in headerNames:
            self.headers.pop(key)

    def updateContextState(self, videoId=None, replacables={}, additional={}, removables=[]):
        if videoId is not None:
            self.__Context.replaceVideoId(videoId)
        for key, val in replacables.items():
            if key in self.__Context:
                self.__Context[key] = val
            else:
                self.__Context.replace(key, val)

        for key, val in additional.items():
            self.__Context.add(key, val)

        for key in removables:
            if key in self.__Context.get():
                self.__Context.remove(key)
            else:
                self.__Context.replace(key, '')

    def send(self, url, method="GET", additional_payload=None):

        if type(method) != str or method not in ["GET", "POST"]:
            raise ValueError(
                "Invalid 'method' value. must be either 'GET' or 'POST'")

        # if type(payload) != dict:
        #     raise ValueError("Invalid 'payload' value. must be a dictionary")

        if type(url) != str:
            raise ValueError("Invalid 'url' value. must be a string")

        # Merge payloads
        payload = self.__Context.get()
        # if additional_payload is not None and type(additional_payload) == dict:
        #     payt
        #     payload.update(additional_payload)
        if method.upper() == "GET":
            response = requests.get(url, headers = {
                "Accept":"text/html"
            })

        elif method.upper() == "POST":
            response = requests.post(
                url,
                json=payload,
                headers=self.headers
            )

        if response.status_code == 200:
            if method.upper() == "GET":
                return response
            elif method.upper() == "POST":
                return response.json()
        else:
            # print(response.content)
            raise RuntimeError(f"Request failed ({response.status_code})")
        return None

