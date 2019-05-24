from datetime import date
from java.nio.file import Paths
from java.lang import Integer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from urllib.parse import unquote_plus
import re


def create_query(dmy, typ, period="year", site_id=None, segment=None, handle=None):
    q = "+type: " + typ
    if dmy:
        dmy = [int(x) for x in dmy]

        if period == 'year' and len(dmy) > 0:
            q += " AND +year: " + str(dmy[0])
        elif period == 'month':
            if len(dmy) == 1:
                q += " AND +year: " + str(dmy[0])
            elif len(dmy) > 1:
                q += " AND +year: " + str(dmy[0]) + " AND +month: " + str(dmy[1])
        elif period == 'day':
            if len(dmy) == 1:
                q += " AND +year: " + str(dmy[0])
            elif len(dmy) == 2:
                q += " AND +year: " + str(dmy[0]) + " AND +month: " + str(dmy[1])
            elif len(dmy) == 3:
                q += " AND +year: " + str(dmy[0]) + " AND +month: " + str(dmy[1]) + " AND +day: " + str(dmy[2])

    q += " AND +period: " + period
    if site_id:
        if isinstance(site_id, list):
            q += " AND +site_id: (" + " OR ".join(str(s) for s in site_id) + ")"
        else:
            q += " AND +site_id: " + str(site_id)
    else:
        q += " AND +site_id: [* TO *]"

    if segment:
        q += ' AND +segment: "' + segment + '"'
    else:
        q += ' AND -segment: [* TO *]'

    if handle:
        q += ' AND +handle: "' + handle + '"'

    return q


class Searcher(object):

    def __init__(self, index="indexes"):
        self.initialized = False
        self.initialize(index)

    def initialize(self, index="indexes"):
        if DirectoryReader.indexExists(SimpleFSDirectory(Paths.get(index))):
            self.directory = DirectoryReader.open(SimpleFSDirectory(Paths.get(index)))
            self.searcher = IndexSearcher(self.directory)
            self.analyzer = WhitespaceAnalyzer()
            self.parser = QueryParser("type", self.analyzer)
            self.initialized = True

    def search(self, query):
        if not self.initialized:
            self.initialize()
        if self.initialized:
            q = self.parser.parse(query)
            results = self.searcher.search(q, Integer.MAX_VALUE)
            hits = results.scoreDocs
            return [self.searcher.doc(hit.doc) for hit in hits]
        else:
            return []

    def search_views(self, dmy=None, period='year', site_id=None, segment=None):

        q = create_query(dmy, "views", period=period, site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()

        if period == 'year':
            results["total"] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}

        for doc in docs:
            nb_pageviews = int(doc["nb_pageviews"])
            nb_uniq_pageviews = int(doc["nb_uniq_pageviews"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            period = doc["period"]
            if period == 'year':
                if year not in results:
                    results[year] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
                results[year]["nb_pageviews"] += nb_pageviews
                results[year]["nb_uniq_pageviews"] += nb_uniq_pageviews
                results["total"]["nb_pageviews"] += nb_pageviews
                results["total"]["nb_uniq_pageviews"] += nb_uniq_pageviews
            elif period == 'month':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
                results[year][month]["nb_pageviews"] += nb_pageviews
                results[year][month]["nb_uniq_pageviews"] += nb_uniq_pageviews
            elif period == 'day':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if day not in results[year][month]:
                    results[year][month][day] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
                results[year][month][day]["nb_pageviews"] += nb_pageviews
                results[year][month][day]["nb_uniq_pageviews"] += nb_uniq_pageviews
        return results

    def search_visits(self, dmy=None, period='year', site_id=None, segment=None):

        q = create_query(dmy, "visits", period=period, site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()

        if period == 'year':
            results["total"] = {"nb_visits": 0, "nb_uniq_visitors": 0}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_uniq_visitors = 0
            if doc["nb_uniq_visitors"]:
                nb_uniq_visitors = int(doc["nb_uniq_visitors"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            period = doc["period"]
            if period == 'year':
                if year not in results:
                    results[year] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year]["nb_visits"] += nb_visits
                results[year]["nb_uniq_visitors"] += nb_uniq_visitors
                results["total"]["nb_visits"] += nb_visits
                results["total"]["nb_uniq_visitors"] += nb_uniq_visitors
            elif period == 'month':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year][month]["nb_visits"] += nb_visits
                results[year][month]["nb_uniq_visitors"] += nb_uniq_visitors
            elif period == 'day':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if day not in results[year][month]:
                    results[year][month][day] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year][month][day]["nb_visits"] += nb_visits
                results[year][month][day]["nb_uniq_visitors"] += nb_uniq_visitors

        return results

    def close(self):
        self.directory.close()

    def search_country(self, dmy=None, period='year', site_id=None, segment=None):

        q = create_query(dmy, "country", period=period, site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()

        if period == 'year':
            results["total"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_uniq_visitors = 0
            if doc["nb_uniq_visitors"]:
                nb_uniq_visitors = int(doc["nb_uniq_visitors"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            period = doc["period"]
            country = doc["country"]
            if period == 'year':
                if year not in results:
                    results[year] = {}
                if country not in results[year]:
                    results[year][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                if country not in results["total"]:
                    results["total"][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year][country]["nb_visits"] += nb_visits
                results[year][country]["nb_uniq_visitors"] += nb_uniq_visitors
                results["total"][country]["nb_visits"] += nb_visits
                results["total"][country]["nb_uniq_visitors"] += nb_uniq_visitors
            elif period == 'month':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if country not in results[year][month]:
                    results[year][month][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year][month][country]["nb_visits"] += nb_visits
                results[year][month][country]["nb_uniq_visitors"] += nb_uniq_visitors
            elif period == 'day':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if day not in results[year][month]:
                    results[year][month][day] = {}
                if country not in results[year][month][day]:
                    results[year][month][day][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results[year][month][day][country]["nb_visits"] += nb_visits
                results[year][month][day][country]["nb_uniq_visitors"] += nb_uniq_visitors

        return results

    def search_urls(self, dmy=None, period='year', site_id=None, segment=None):

        q = create_query(dmy, "urls", period=period, site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()

        if period == 'year':
            results["total"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_hits = 0
            if doc["nb_hits"]:
                nb_hits = int(doc["nb_hits"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            period = doc["period"]

            if "url" in doc:
                url = unquote_plus(doc["url"]).split("?")[0]
            else:
                url = unquote_plus(doc["label"]).split("?")[0]

            if ".continue" in url:
                url = "/".join(url.split("/")[:-1])

            if url.startswith("services"):
                if url.startswith("services/treex-web/api/v1/results"):
                    url = "services/treex-web/api/v1/results"
                if url.startswith("services/treex-web/result"):
                    url = "services/treex-web/result"

                url = re.sub(r'(services/pmltq/index#!/treebank/.+/query)/.+', '\\1', url)

            url = re.sub(r'/(\./)+', '/', url)

            if period == 'year':
                if year not in results:
                    results[year] = {}
                if url not in results[year]:
                    results[year][url] = {"nb_visits": 0, "nb_hits": 0}
                if url not in results["total"]:
                    results["total"][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][url]["nb_visits"] += nb_visits
                results[year][url]["nb_hits"] += nb_hits
                results["total"][url]["nb_visits"] += nb_visits
                results["total"][url]["nb_hits"] += nb_hits
            elif period == 'month':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if url not in results[year][month]:
                    results[year][month][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][month][url]["nb_visits"] += nb_visits
                results[year][month][url]["nb_hits"] += nb_hits
            elif period == 'day':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if day not in results[year][month]:
                    results[year][month][day] = {}
                if url not in results[year][month][day]:
                    results[year][month][day][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][month][day][url]["nb_visits"] += nb_visits
                results[year][month][day][url]["nb_hits"] += nb_hits

        return results

    def search_handle(self, dmy=None, period='year', site_id=None, handle=None, segment=None):

        q = create_query(dmy, "urls", period=period, site_id=site_id, handle=handle, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()

        if period == 'year':
            results["total"] = {"nb_visits": 0, "nb_hits": 0}
        else:
            results["total"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_hits = 0
            if doc["nb_hits"]:
                nb_hits = int(doc["nb_hits"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            period = doc["period"]

            if "url" in doc:
                url = unquote_plus(doc["url"]).split("?")[0]
            else:
                url = unquote_plus(doc["label"]).split("?")[0]

            if period == 'year':
                if year not in results:
                    results[year] = {}
                if url not in results[year]:
                    results[year][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][url]["nb_visits"] += nb_visits
                results[year][url]["nb_hits"] += nb_hits

                if year not in results["total"]:
                    results["total"][year] = {"nb_visits": 0, "nb_hits": 0}
                results["total"]["nb_visits"] += nb_visits
                results["total"]["nb_hits"] += nb_hits
                results["total"][year]["nb_visits"] += nb_visits
                results["total"][year]["nb_hits"] += nb_hits

            elif period == 'month':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if url not in results[year][month]:
                    results[year][month][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][month][url]["nb_visits"] += nb_visits
                results[year][month][url]["nb_hits"] += nb_hits

                if year not in results["total"]:
                    results["total"][year] = {}
                if month not in results["total"][year]:
                    results["total"][year][month] = {"nb_visits": 0, "nb_hits": 0}
                results["total"][year][month]["nb_visits"] += nb_visits
                results["total"][year][month]["nb_hits"] += nb_hits

            elif period == 'day':
                if year not in results:
                    results[year] = {}
                if month not in results[year]:
                    results[year][month] = {}
                if day not in results[year][month]:
                    results[year][month][day] = {}
                if url not in results[year][month][day]:
                    results[year][month][day][url] = {"nb_visits": 0, "nb_hits": 0}
                results[year][month][day][url]["nb_visits"] += nb_visits
                results[year][month][day][url]["nb_hits"] += nb_hits

                if year not in results["total"]:
                    results["total"][year] = {}
                if month not in results["total"][year]:
                    results["total"][year][month] = {}
                if day not in results["total"][year][month]:
                    results["total"][year][month][day] = {"nb_visits": 0, "nb_hits": 0}
                results["total"][year][month][day]["nb_visits"] += nb_visits
                results["total"][year][month][day]["nb_hits"] += nb_hits

        return results

    def close(self):
        self.directory.close()

