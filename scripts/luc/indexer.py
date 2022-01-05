import os
import re
import hashlib
from urllib.parse import quote_plus
from java.nio.file import Paths
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, StoredField, IntPoint, StringField
from org.apache.lucene.index import FieldInfo, IndexWriter, IndexWriterConfig, IndexOptions, Term
from org.apache.lucene.store import SimpleFSDirectory


class Indexer(object):

    def __init__(self, index="indexes"):
        if not os.path.exists(index):
            os.mkdir(index)
        self.store = SimpleFSDirectory(Paths.get(index))
        self.analyzer = WhitespaceAnalyzer()
        self.config = IndexWriterConfig(self.analyzer)
        self.config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
        self.writer = IndexWriter(self.store, self.config)

    def index_views(self, site_id, date, row, segment=None):
        try:
            doc, q = Indexer.initialize_document(site_id, date, "views", segment)
            doc_id = hashlib.sha1(q.encode('UTF-8')).hexdigest()
            doc.add(StringField("id", doc_id, Field.Store.NO))
            doc.add(StoredField("nb_pageviews", int(row["nb_pageviews"])))
            doc.add(StoredField("nb_uniq_pageviews", int(row["nb_uniq_pageviews"])))
            self.writer.updateDocument(Term("id", doc_id), doc)
        except:
            self.writer.rollback()
            print("Failed in index_views")
            raise

    def index_visits(self, site_id, date, row, segment=None):
        try:
            doc, q = Indexer.initialize_document(site_id, date, "visits", segment)
            doc_id = hashlib.sha1(q.encode('UTF-8')).hexdigest()
            doc.add(StringField("id", doc_id, Field.Store.NO))
            if type(row) is dict:
                doc.add(StoredField("nb_visits", int(row["nb_visits"])))
                if "nb_uniq_visitors" in row:
                    doc.add(StoredField("nb_uniq_visitors", int(row["nb_uniq_visitors"])))
            else:
                doc.add(StoredField("nb_visits", int(row)))
            self.writer.updateDocument(Term("id", doc_id), doc)
        except:
            self.writer.rollback()
            print("Failed in index_visits")
            raise

    def index_country(self, site_id, date, row, segment=None, add=False):
        try:
            ft1 = FieldType()
            ft1.setStored(True)
            ft1.setIndexOptions(IndexOptions.DOCS)
            for r in row:
                doc, q = Indexer.initialize_document(site_id, date, "country", segment)
                doc.add(Field("country", r["code"], ft1))
                q += " AND +country: " + r["code"]
                doc_id = hashlib.sha1(q.encode('UTF-8')).hexdigest()
                doc.add(StringField("id", doc_id, Field.Store.NO))
                doc.add(StoredField("nb_visits", int(r["nb_visits"])))
                if "nb_uniq_visitors" in r:
                    doc.add(StoredField("nb_uniq_visitors", int(r["nb_uniq_visitors"])))
                self.writer.updateDocument(Term("id", doc_id), doc)
        except:
            self.writer.rollback()
            print("Failed in index_country")
            raise

    def index_urls(self, site_id, date, row, segment=None, add=False):
        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)
        try:
            for r in row:
                doc, q = Indexer.initialize_document(site_id, date, "urls", segment)
                doc.add(Field("label", quote_plus(r["label"]), ft1))
                q += ' AND +label: ' + quote_plus(r["label"])

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

                doc.add(StoredField("nb_visits", int(r["nb_visits"])))
                doc.add(StoredField("nb_hits", int(r["nb_hits"])))

                doc_id = hashlib.sha1(q.encode('UTF-8')).hexdigest()
                doc.add(StringField("id", doc_id, Field.Store.NO))
                self.writer.updateDocument(Term("id", doc_id), doc)
        except:
            self.writer.rollback()
            print("Failed in index_urls")
            raise

    def close(self):
        self.writer.commit()
        self.writer.close()

    @staticmethod
    def initialize_document(site_id, date, ty, segment=None):
        y = m = d = None
        q = ""
        ft1 = FieldType()
        ft1.setStored(True)
        ft1.setIndexOptions(IndexOptions.DOCS)
        doc = Document()
        if len(date) == 3:
            y = int(date[0])
            m = int(date[1])
            d = int(date[2])
            doc.add(Field("period", "day", ft1))
            doc.add(Field("year", str(y), ft1))
            doc.add(Field("month", str(m), ft1))
            doc.add(Field("day", str(d), ft1))
            q = "+period: day AND +year: " + str(y) + " AND +month: " + str(m) + " AND +day: " + str(d)
        elif len(date) == 2:
            y = int(date[0])
            m = int(date[1])
            doc.add(Field("period", "month", ft1))
            doc.add(Field("year", str(y), ft1))
            doc.add(Field("month", str(m), ft1))
            q = "+period: month AND +year: " + str(y) + " AND +month: " + str(m)
        elif len(date) == 1:
            y = int(date[0])
            doc.add(Field("period", "year", ft1))
            doc.add(Field("year", str(y), ft1))
            q = "+period: year AND +year: " + str(y)
        doc.add(Field("site_id", site_id, ft1))
        doc.add(Field("type", ty, ft1))
        if segment:
            doc.add(Field("segment", segment, ft1))
            q += ' AND +segment: "' + segment + '"'
        else:
            q += ' AND -segment: [* TO *]'
        q += " AND +site_id: " + site_id + " AND +type: " + ty
        return doc, q
