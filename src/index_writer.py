""" Batch index collection of documents """

from datetime import datetime
import lucene
from pandas import read_csv

# pylint: disable=import-error
from java.nio.file import Paths
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, TextField, LongPoint, StringField


def date2long(date):
    """ convert cord19 datetime format to long int for lucene"""
    if len(date) == 4:
        # only year
        parsed = int(f"{date}0101")
    else:
        # year-month-day
        parsed = int(datetime.strptime(date, '%Y-%m-%d').strftime('%Y%m%d'))
    return parsed


class Indexer():
    """something
    """
    def __init__(self, store_path: str, create_mode=False):
        self.store_path = store_path
        self.create_mode = create_mode

    def __create_index_writer(self, store: SimpleFSDirectory) -> IndexWriter:
        analyzer = StandardAnalyzer()
        config = IndexWriterConfig(analyzer)
        if self.create_mode:
            config.setOpenMode(IndexWriterConfig.OpenMode.CREATE)
        index_writer = IndexWriter(store, config)
        return index_writer

    def index_from_dataframe(self, dataframe):
        """ index elements in dataframe"""
        fields = {
            'cord_uid': StringField.TYPE_NOT_STORED,
            'source_x': TextField.TYPE_STORED,
            'title': TextField.TYPE_STORED,
            'abstract': TextField.TYPE_STORED,
            'publish_time': LongPoint,
            'journal': TextField.TYPE_STORED,
            'authors': TextField.TYPE_STORED,
            'url': TextField.TYPE_STORED
        }

        store = SimpleFSDirectory(Paths.get(self.store_path))
        writer = self.__create_index_writer(store)

        try:
            for _, row, in dataframe.iterrows():
                document = Document()
                for key, val in fields.items():
                    if val == LongPoint:
                        date_millis = date2long(row[key])
                        document.add(LongPoint(key, date_millis))
                        document.add(
                            Field("publish", row[key],
                                  StringField.TYPE_STORED))
                    else:
                        document.add(Field(key, row[key], val))
                writer.addDocument(document)
        finally:
            writer.close()
            store.close()
            print("finish")


if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])

    INDEXPATH = '/home/jtt/Documents/indexes/cord19'
    CSVPATH = '/home/jtt/repos/bio-search/2022-02-07-cord19.csv'

    df = read_csv(CSVPATH)
    df = df.reset_index()
    df = df.dropna()
    print(df.shape)

    indexer = Indexer(INDEXPATH, create_mode=True)
    indexer.index_from_dataframe(dataframe=df)
