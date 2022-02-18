from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version
from org.apache.lucene.document import Document, Field, TextField
from org.apache.lucene.search import IndexSearcher


class Indexer():
    """something
    """
    def __init__(self, store_path: str, create_mode=False):
        self.store = SimpleFSDirectory(Paths.get(store_path))
        self.create_mode = create_mode
        self.writer = self.__create_index_writer()

    def __create_index_writer(self):
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        if self.create_mode:
            config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        index_writer = IndexWriter(self.store, config)
        return index_writer

    def index_from_dataframe(self, df):
        pass
