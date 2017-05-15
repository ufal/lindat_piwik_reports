import os
import re
from urllib.parse import quote_plus
from java.nio.file import Paths
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StoredField, IntPoint
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from luc import searcher


class Indexer(object):

    def __init__(self, index="indexes"):
        if not os.path.exists(index):
            os.mkdir(index)
        self.store = SimpleFSDirectory(Paths.get(index))
        self.analyzer = WhitespaceAnalyzer()
        self.config = IndexWriterConfig(self.analyzer)
        self.config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        self.writer = IndexWriter(self.store, self.config)
        self.parser = QueryParser("type", self.analyzer)
        self.searcher = searcher.Searcher()

    def index_views(self, site_id, date, row, segment=None, add=False):
        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)
        try:
            q = ""
            y = int(date[0])
            m = int(date[1])
            d = int(date[2])
            doc = Document()
            doc.add(Field("type", "views", ft1))
            doc.add(Field("site_id", site_id, ft1))
            doc.add(Field("year", str(y), ft1))
            doc.add(Field("month", str(m), ft1))
            doc.add(Field("day", str(d), ft1))
            if segment:
                doc.add(Field("segment", segment, ft1))
                q = '+segment: "' + segment + '" AND '
            else:
                q = '-segment: [* TO *] AND '

            q += "+site_id: " + site_id + " AND +type: views AND +year: " + str(y) + " AND +month: " + str(m) \
                + " AND +day: " + str(d)

            if add:
                d = self.searcher.search(q)
                nb_pageviews = nb_uniq_pageviews = 0
                if len(d) > 0:
                    nb_pageviews = d[0]["nb_pageviews"]
                    nb_uniq_pageviews = d[0]["nb_uniq_pageviews"]
                doc.add(StoredField("nb_pageviews", int(row["nb_pageviews"]) + int(nb_pageviews)))
                doc.add(StoredField("nb_uniq_pageviews", int(row["nb_uniq_pageviews"]) + int(nb_uniq_pageviews)))
            else:
                doc.add(StoredField("nb_pageviews", int(row["nb_pageviews"])))
                doc.add(StoredField("nb_uniq_pageviews", int(row["nb_uniq_pageviews"])))
            self.writer.deleteDocuments(self.parser.parse(q))
            self.writer.addDocument(doc)
            self.writer.commit()
        except:
            print("Failed in index_views")
            raise

    def index_visits(self, site_id, date, row, segment=None, add=False):
        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)
        try:
            q = ""
            y = int(date[0])
            m = int(date[1])
            d = int(date[2])
            doc = Document()
            doc.add(Field("type", "visits", ft1))
            doc.add(Field("site_id", site_id, ft1))
            doc.add(Field("year", str(y), ft1))
            doc.add(Field("month", str(m), ft1))
            doc.add(Field("day", str(d), ft1))
            if segment:
                doc.add(Field("segment", segment, ft1))
                q = '+segment: "' + segment + '" AND '
            else:
                q = '-segment: [* TO *] AND '

            q += "+site_id: " + site_id + " AND +type: visits AND +year: " + str(y) + " AND +month: " + str(m) \
                + " AND +day: " + str(d)

            if add:
                d = self.searcher.search(q)
                nb_visits = nb_uniq_visitors = 0
                if len(d) > 0:
                    nb_visits = d[0]["nb_visits"]
                    nb_uniq_visitors = d[0]["nb_uniq_visitors"]
                doc.add(StoredField("nb_visits", int(row["nb_visits"]) + int(nb_visits)))
                doc.add(StoredField("nb_uniq_visitors", int(row["nb_uniq_visitors"]) + int(nb_uniq_visitors)))
            else:
                doc.add(StoredField("nb_visits", int(row["nb_visits"])))
                doc.add(StoredField("nb_uniq_visitors", int(row["nb_uniq_visitors"])))
            self.writer.deleteDocuments(self.parser.parse(q))
            self.writer.addDocument(doc)
            self.writer.commit()
        except:
            print("Failed in index_visits")
            raise

    def index_country(self, site_id, date, row, segment=None, add=False):

        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)

        try:
            for r in row:
                q = ""
                y = int(date[0])
                m = int(date[1])
                d = int(date[2])
                doc = Document()
                doc.add(Field("type", "country", ft1))
                doc.add(Field("site_id", site_id, ft1))
                doc.add(Field("year", str(y), ft1))
                doc.add(Field("month", str(m), ft1))
                doc.add(Field("day", str(d), ft1))
                doc.add(Field("country", r["code"], ft1))

                if segment:
                    doc.add(Field("segment", segment, ft1))
                    q = '+segment: "' + segment + '" AND '
                else:
                    q = '-segment: [* TO *] AND '

                q += "+site_id: " + site_id + " AND +type: country AND +year: " + str(y) + " AND +month: " + str(m) \
                    + " AND +day: " + str(d) + " AND +country: " + r["code"]

                if add:
                    d = self.searcher.search(q)
                    nb_visits = nb_uniq_visitors = 0
                    if len(d) > 0:
                        nb_visits = d[0]["nb_visits"]
                        nb_uniq_visitors = d[0]["nb_uniq_visitors"]
                    doc.add(StoredField("nb_visits", int(r["nb_visits"]) + int(nb_visits)))
                    doc.add(StoredField("nb_uniq_visitors", int(r["nb_uniq_visitors"]) + int(nb_uniq_visitors)))
                else:
                    doc.add(StoredField("nb_visits", int(r["nb_visits"])))
                    doc.add(StoredField("nb_uniq_visitors", int(r["nb_uniq_visitors"])))
                self.writer.deleteDocuments(self.parser.parse(q))
                self.writer.addDocument(doc)
            self.writer.commit()
        except:
            print("Failed in index_country")
            raise

    def index_urls(self, site_id, date, row, segment=None, add=False):
        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)
        try:
            for r in row:
                q = ""
                y = int(date[0])
                m = int(date[1])
                d = int(date[2])
                doc = Document()
                doc.add(Field("type", "urls", ft1))
                doc.add(Field("site_id", site_id, ft1))
                doc.add(Field("year", str(y), ft1))
                doc.add(Field("month", str(m), ft1))
                doc.add(Field("day", str(d), ft1))
                doc.add(Field("label", quote_plus(r["label"]), ft1))

                if segment:
                    doc.add(Field("segment", segment, ft1))
                    q = '+segment: "' + segment + '" AND '
                else:
                    q = '-segment: [* TO *] AND '

                q += '+site_id: ' + site_id + ' AND +type: urls AND +year: ' + str(y) + ' AND +month: ' + str(m) \
                    + ' AND +day: ' + str(d) + ' AND +label: ' + quote_plus(r["label"])

                handle = ""
                if "url" in r and r["url"]:
                    doc.add(Field("url", quote_plus(r["url"]), ft1))
                    q += ' AND +url: ' + quote_plus(r["url"])
                    handle = r["url"]
                else:
                    handle = r["label"]

                if "/handle/" in handle:
                    handle = handle[handle.index("/handle/"):]
                    handle = "/".join(re.split("/|\?", handle)[2:4])
                    doc.add(Field("handle", handle, ft1))

                if add:
                    d = self.searcher.search(q)
                    nb_visits = nb_hits = 0
                    if len(d) > 0:
                        nb_visits = d[0]["nb_visits"]
                        nb_hits = d[0]["nb_hits"]
                    doc.add(StoredField("nb_visits", int(r["nb_visits"]) + int(nb_visits)))
                    doc.add(StoredField("nb_hits", int(r["nb_hits"]) + int(nb_hits)))
                else:
                    doc.add(StoredField("nb_visits", int(r["nb_visits"])))
                    doc.add(StoredField("nb_hits", int(r["nb_hits"])))

                self.writer.deleteDocuments(self.parser.parse(q))
                self.writer.addDocument(doc)
            self.writer.commit()
        except:
            print("Failed in index_urls")
            raise

    def close(self):
        self.writer.close()

