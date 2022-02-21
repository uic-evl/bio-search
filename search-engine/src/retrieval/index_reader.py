""" Search the indexes """
from datetime import datetime
from typing import List

import lucene
# pylint: disable=import-error
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.document import LongPoint
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.search import IndexSearcher, BooleanClause, BooleanQuery
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser

from .search_results import SearchResult


def strdate2long(date: str) -> int:
    """ concatenate year month day to int to search index by long representation """
    return int(datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d'))


class Reader():
    """ search indexes """
    def __init__(self, store_path: str):
        self.store_path = store_path

    def search(self,
               terms: str,
               start_date: str,
               end_date: str,
               modalities: List[str],
               only_with_images=False,
               max_docs=10) -> List[SearchResult]:
        """ search index by fields"""
        index_dir = SimpleFSDirectory(Paths.get(self.store_path))
        dir_reader = DirectoryReader.open(index_dir)
        searcher = IndexSearcher(dir_reader)

        try:
            if start_date or end_date:
                if start_date and end_date:
                    query_date_from = strdate2long(start_date)
                    query_date_to = strdate2long(end_date)
                elif start_date and not end_date:
                    query_date_from = strdate2long(start_date)
                    query_date_to = strdate2long(start_date)
                range_query = LongPoint.newRangeQuery("publish_time",
                                                      query_date_from,
                                                      query_date_to)
            else:
                range_query = None

            query_builder = BooleanQuery.Builder()
            parser = QueryParser("default", StandardAnalyzer())
            if terms:
                text_query = parser.parse(
                    f"title: {terms} OR abstract:{terms}")
                query_builder.add(text_query, BooleanClause.Occur.MUST)

            if range_query:
                query_builder.add(range_query, BooleanClause.Occur.MUST)

            if modalities:
                mod_query = None
                for modality in modalities:
                    if not mod_query:
                        mod_query = f"modality:{modality}"
                    else:
                        mod_query = f"{mod_query} OR {modality}"
                query_builder.add(parser.parse(mod_query),
                                  BooleanClause.Occur.MUST)

            if only_with_images:
                query_builder.add(parser.parse("modality:[a* TO z*]"),
                                  BooleanClause.Occur.MUST)

            boolean_query = query_builder.build()
            hits = searcher.search(boolean_query, max_docs).scoreDocs
            results = []
            for hit in hits:
                hit_doc = searcher.doc(hit.doc)

                modalities = [
                    x.stringValue() for x in hit_doc.getFields("modality")
                ]
                result = SearchResult(title=hit_doc.get("title"),
                                      abstract=hit_doc.get("abstract"),
                                      publish_date=hit_doc.get("publish"),
                                      modalities=modalities)
                results.append(result)
            return results
        finally:
            dir_reader.close()


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print("todo")
