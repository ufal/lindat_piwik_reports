from enum import Enum
import requests
import urllib.parse


class Analytics(object):

    def __init__(self, url=None, token_auth=None, id_site=1):
        self.url = url
        self.params = dict()
        self.params["idSite"] = id_site
        self.params["token_auth"] = token_auth
        self.params["module"] = "API"
        self.params["method"] = "Actions.get"
        self.params["period"] = Period.DAY.value
        self.params["date"] = "today"
        self.params["format"] = Format.JSON.value

    def set_param(self, name, val):
        self.params[name] = val

    def get_param(self, name):
        return self.params[name]

    def get(self):
        print(self.url + "?" + urllib.parse.urlencode(self.params))
        response = requests.get(self.url, params=self.params)
        return response.json()


class Period(Enum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"
    RANGE = "range"


class Format(Enum):
    XML = "xml"
    JSON = "json"
    CSV = "csv"
    TSV = "tsv"
    HTML = "html"
    PHP = "php"
    RSS = "rss"
    ORIGINAL = "original"
