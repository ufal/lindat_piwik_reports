from datetime import date
from java.nio.file import Paths
from java.lang import Integer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from urllib.parse import unquote_plus


def create_query(dmy, typ, site_id=None, segment=None, handle=None):
    q = "+type: " + typ
    if dmy:
        dmy = [int(x) for x in dmy]
        q += " AND +year: " + str(dmy[0])
        if len(dmy) > 1:
            q += " AND +month: " + str(dmy[1])
        if len(dmy) > 2:
            q += " AND +day: " + str(dmy[2])

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

    def __init__(self):
        self.initialized = False
        self.initialize()

    def initialize(self):
        if DirectoryReader.indexExists(SimpleFSDirectory(Paths.get("indexes"))):
            self.directory = DirectoryReader.open(SimpleFSDirectory(Paths.get("indexes")))
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

    def search_views(self, dmy, site_id=None, segment=None):

        q = create_query(dmy, "views",  site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()
        results["total"] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
        results["years"] = {}

        for doc in docs:
            nb_pageviews = int(doc["nb_pageviews"])
            nb_uniq_pageviews = int(doc["nb_uniq_pageviews"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            if year not in results["years"]:
                results["years"][year] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
                results["years"][year]["months"] = {}
            if month not in results["years"][year]["months"]:
                results["years"][year]["months"][month] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}
                results["years"][year]["months"][month]["days"] = {}
            if day not in results["years"][year]["months"][month]["days"]:
                results["years"][year]["months"][month]["days"][day] = {"nb_pageviews": 0, "nb_uniq_pageviews": 0}

            results["total"]["nb_pageviews"] += nb_pageviews
            results["total"]["nb_uniq_pageviews"] += nb_uniq_pageviews

            results["years"][year]["nb_pageviews"] += nb_pageviews
            results["years"][year]["nb_uniq_pageviews"] += nb_uniq_pageviews

            results["years"][year]["months"][month]["nb_pageviews"] += nb_pageviews
            results["years"][year]["months"][month]["nb_uniq_pageviews"] += nb_uniq_pageviews

            results["years"][year]["months"][month]["days"][day]["nb_pageviews"] += nb_pageviews
            results["years"][year]["months"][month]["days"][day]["nb_uniq_pageviews"] += nb_uniq_pageviews

        return results

    def search_visits(self, dmy, site_id=None, segment=None):

        q = create_query(dmy, "visits", site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()
        results["total"] = {"nb_visits": 0, "nb_uniq_visitors": 0}
        results["years"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_uniq_visitors = int(doc["nb_uniq_visitors"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            if year not in results["years"]:
                results["years"][year] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results["years"][year]["months"] = {}
            if month not in results["years"][year]["months"]:
                results["years"][year]["months"][month] = {"nb_visits": 0, "nb_uniq_visitors": 0}
                results["years"][year]["months"][month]["days"] = {}
            if day not in results["years"][year]["months"][month]["days"]:
                results["years"][year]["months"][month]["days"][day] = {"nb_visits": 0, "nb_uniq_visitors": 0}

            results["total"]["nb_visits"] += nb_visits
            results["total"]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year]["nb_visits"] += nb_visits
            results["years"][year]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year]["months"][month]["nb_visits"] += nb_visits
            results["years"][year]["months"][month]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year]["months"][month]["days"][day]["nb_visits"] += nb_visits
            results["years"][year]["months"][month]["days"][day]["nb_uniq_visitors"] += nb_uniq_visitors

        return results

    def close(self):
        self.directory.close()

    def search_country(self, dmy, site_id=None, segment=None):

        q = create_query(dmy, "country", site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()
        results["total"] = {}
        results["years"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_uniq_visitors = int(doc["nb_uniq_visitors"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            country = doc["country"]
            if country not in results["total"]:
                results["total"][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
            if year not in results["years"]:
                results["years"][year] = {}
                results["years"][year]["months"] = {}
            if country not in results["years"][year]:
                results["years"][year][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
            if month not in results["years"][year]["months"]:
                results["years"][year]["months"][month] = {}
                results["years"][year]["months"][month]["days"] = {}
            if country not in results["years"][year]["months"][month]:
                results["years"][year]["months"][month][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}
            if day not in results["years"][year]["months"][month]["days"]:
                results["years"][year]["months"][month]["days"][day] = {}
            if country not in results["years"][year]["months"][month]["days"][day]:
                results["years"][year]["months"][month]["days"][day][country] = {"nb_visits": 0, "nb_uniq_visitors": 0}

            results["total"][country]["nb_visits"] += nb_visits
            results["total"][country]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year][country]["nb_visits"] += nb_visits
            results["years"][year][country]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year]["months"][month][country]["nb_visits"] += nb_visits
            results["years"][year]["months"][month][country]["nb_uniq_visitors"] += nb_uniq_visitors

            results["years"][year]["months"][month]["days"][day][country]["nb_visits"] += nb_visits
            results["years"][year]["months"][month]["days"][day][country]["nb_uniq_visitors"] += nb_uniq_visitors

        return results

    def search_urls(self, dmy, site_id=None, segment=None):

        q = create_query(dmy, "urls", site_id=site_id, segment=segment)
        print(q)
        docs = self.search(q)

        results = dict()
        results["total"] = {}
        results["years"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_hits = int(doc["nb_hits"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            if "url" in doc:
                url = unquote_plus(doc["url"]).split("?")[0]
            else:
                url = unquote_plus(doc["label"]).split("?")[0]
            if url not in results["total"]:
                results["total"][url] = {"nb_visits": 0, "nb_hits": 0}
            if year not in results["years"]:
                results["years"][year] = {}
                results["years"][year]["months"] = {}
            if url not in results["years"][year]:
                results["years"][year][url] = {"nb_visits": 0, "nb_hits": 0}
            if month not in results["years"][year]["months"]:
                results["years"][year]["months"][month] = {}
                results["years"][year]["months"][month]["days"] = {}
            if url not in results["years"][year]["months"][month]:
                results["years"][year]["months"][month][url] = {"nb_visits": 0, "nb_hits": 0}
            if day not in results["years"][year]["months"][month]["days"]:
                results["years"][year]["months"][month]["days"][day] = {}
            if url not in results["years"][year]["months"][month]["days"][day]:
                results["years"][year]["months"][month]["days"][day][url] = {"nb_visits": 0, "nb_hits": 0}

            results["total"][url]["nb_visits"] += nb_visits
            results["total"][url]["nb_hits"] += nb_hits

            results["years"][year][url]["nb_visits"] += nb_visits
            results["years"][year][url]["nb_hits"] += nb_hits

            results["years"][year]["months"][month][url]["nb_visits"] += nb_visits
            results["years"][year]["months"][month][url]["nb_hits"] += nb_hits

            results["years"][year]["months"][month]["days"][day][url]["nb_visits"] += nb_visits
            results["years"][year]["months"][month]["days"][day][url]["nb_hits"] += nb_hits

        return results

    def search_handle(self, dmy, site_id=None, handle=None):

        q = create_query(dmy, "urls", site_id=site_id, handle=handle)
        print(q)
        docs = self.search(q)

        results = dict()
        results["total"] = {}
        results["years"] = {}

        for doc in docs:
            nb_visits = int(doc["nb_visits"])
            nb_hits = int(doc["nb_hits"])
            year = doc["year"]
            month = doc["month"]
            day = doc["day"]
            if "url" in doc:
                url = unquote_plus(doc["url"]).split("?")[0]
            else:
                url = unquote_plus(doc["label"]).split("?")[0]
            if url not in results["total"]:
                results["total"][url] = {"nb_visits": 0, "nb_hits": 0}
            if year not in results["years"]:
                results["years"][year] = {}
                results["years"][year]["months"] = {}
            if url not in results["years"][year]:
                results["years"][year][url] = {"nb_visits": 0, "nb_hits": 0}
            if month not in results["years"][year]["months"]:
                results["years"][year]["months"][month] = {}
                results["years"][year]["months"][month]["days"] = {}
            if url not in results["years"][year]["months"][month]:
                results["years"][year]["months"][month][url] = {"nb_visits": 0, "nb_hits": 0}
            if day not in results["years"][year]["months"][month]["days"]:
                results["years"][year]["months"][month]["days"][day] = {}
            if url not in results["years"][year]["months"][month]["days"][day]:
                results["years"][year]["months"][month]["days"][day][url] = {"nb_visits": 0, "nb_hits": 0}

            results["total"][url]["nb_visits"] += nb_visits
            results["total"][url]["nb_hits"] += nb_hits

            results["years"][year][url]["nb_visits"] += nb_visits
            results["years"][year][url]["nb_hits"] += nb_hits

            results["years"][year]["months"][month][url]["nb_visits"] += nb_visits
            results["years"][year]["months"][month][url]["nb_hits"] += nb_hits

            results["years"][year]["months"][month]["days"][day][url]["nb_visits"] += nb_visits
            results["years"][year]["months"][month]["days"][day][url]["nb_hits"] += nb_hits

        return results

    def close(self):
        self.directory.close()
