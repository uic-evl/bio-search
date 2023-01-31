""" Search the indexes """
from datetime import datetime
from re import S
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
from org.apache.lucene.search.highlight import (
    SimpleHTMLFormatter,
    QueryScorer,
    Highlighter,
    SimpleSpanFragmenter,
    GradientFormatter,
)
from java.io import StringReader

from .search_results import SearchResult


def strdate2long(date: str) -> int:
    """concatenate year month day to int to search index by long representation"""
    return int(datetime.strptime(date, "%Y-%m-%d").strftime("%Y%m%d"))


class Reader:
    """search indexes"""

    def __init__(self, store_path: str):
        self.store_path = store_path
        self._last_query = None

    def search(
        self,
        terms: str,
        start_date: str,
        end_date: str,
        modalities: List[str],
        only_with_images=False,
        max_docs=10,
        highlight=False,
        ft=False,
    ) -> List[SearchResult]:
        """search index by fields"""
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
                range_query = LongPoint.newRangeQuery(
                    "pub_date", query_date_from, query_date_to
                )
            else:
                range_query = None

            query_builder = BooleanQuery.Builder()
            # making abstract the default field
            parser = QueryParser("abstract", StandardAnalyzer())
            if terms:
                if ":" in terms:
                    # allow passing the whole construct
                    text_query = parser.parse(terms)
                else:
                    # supports search on the first term and rest on default field
                    # or when adding " " to find a longer matching keywords on
                    # the same field
                    query_input = (
                        f"title: {terms} OR abstract:{terms} OR caption:{terms}"
                    )
                    if ft:
                        query_input = f"{query_input} OR full_text={terms}"
                    text_query = parser.parse(query_input)
                query_builder.add(text_query, BooleanClause.Occur.MUST)

            if range_query:
                query_builder.add(range_query, BooleanClause.Occur.MUST)

            if modalities:
                mod_query = None
                for modality in modalities:
                    if not mod_query:
                        # mod_query = f"modality:{modality.replace(' ', '?')}"
                        mod_query = f"modality:{modality}"
                    else:
                        mod_query = f"{mod_query} OR modality:{modality}"
                query_builder.add(parser.parse(mod_query), BooleanClause.Occur.MUST)

            hl_query = query_builder.build()

            # this clause breaks the highlights
            if only_with_images:
                query_builder.add(
                    parser.parse("modality:[a* TO z*]"), BooleanClause.Occur.MUST
                )

            boolean_query = query_builder.build()
            self._last_query = hl_query

            hits = searcher.search(boolean_query, max_docs).scoreDocs
            results = []
            for hit in hits:
                hit_doc = searcher.doc(hit.doc)

                modalities = [x.stringValue() for x in hit_doc.getFields("modality")]

                title = hit_doc.get("title")
                url = hit_doc.get("url")
                abstract = hit_doc.get("abstract")
                num_figures = int(hit_doc.get("num_figures"))
                if highlight:
                    hl_title, hl_abstract, hl_ft = self.get_highlight(hit_doc, ft)
                    title = hl_title or title
                    abstract = hl_abstract or abstract
                    full_text = hl_ft or ""

                captions = self.get_highlighted_captions(hit_doc)

                result = SearchResult(
                    id=hit_doc.get("docId"),
                    title=title,
                    abstract=abstract,
                    publish_date=hit_doc.get("publish"),
                    num_figures=num_figures,
                    modalities=modalities,
                    url=url,
                    full_text=full_text,
                    journal=hit_doc.get("journal"),
                    authors=hit_doc.get("authors"),
                    captions=captions,
                )
                results.append(result)
            return results
        finally:
            dir_reader.close()

    def get_last_query(self):
        """access to the last query performed"""
        return self._last_query

    def get_highlighted_captions(self, document):
        """Get a highlighted section or the whole caption"""
        formatter = SimpleHTMLFormatter()
        scorer = QueryScorer(self._last_query)
        highlighter = Highlighter(formatter, scorer)
        analyzer = StandardAnalyzer()

        fragmenter = SimpleSpanFragmenter(scorer)
        highlighter.setTextFragmenter(fragmenter)

        captions = [x.stringValue() for x in document.getFields("caption")]
        for caption in captions:
            tstream = analyzer.tokenStream("caption", StringReader(caption))
            highlighted = highlighter.getBestFragments(tstream, caption, 3, "...")
            if len(highlighted) > 0:
                print("found")
                caption = highlighted
        return captions

    def get_highlight(self, document, ft):
        """Returns the highlighted title and abstract, if any"""
        formatter = SimpleHTMLFormatter()
        scorer = QueryScorer(self._last_query)
        highlighter = Highlighter(formatter, scorer)
        analyzer = StandardAnalyzer()

        fragmenter = SimpleSpanFragmenter(scorer, 200)
        highlighter.setTextFragmenter(fragmenter)

        title = document.get("title")
        abstract = document.get("abstract")

        ts_title = analyzer.tokenStream("title", StringReader(title))
        frag_title = highlighter.getBestFragments(ts_title, title, 3, "...")

        ts_abs = analyzer.tokenStream("abstract", StringReader(abstract))
        frag_abs = highlighter.getBestFragments(ts_abs, abstract, 3, "...")

        frag_full_text = ""
        if ft:
            full_text = document.get("full_text")
            ts_full_text = analyzer.tokenStream("full_text", StringReader(full_text))
            frag_full_text = highlighter.getBestFragments(
                ts_full_text, full_text, 5, "..."
            )

        title = frag_title if len(frag_title) > 0 else None
        abstract = frag_abs if len(frag_abs) > 0 else None
        full_text = frag_full_text if len(frag_full_text) > 0 else None

        return title, abstract, full_text


if __name__ == "__main__":
    lucene.initVM(vmargs=["-Djava.awt.headless=true"])
    print("todo")
