import requests


class Query:

    def __init__(self):
        self.url = ""
        self.params = {}
        self.headers = {}

    def make_query(self):
        return requests.get(self.url, headers=self.headers, params=self.params).json()
