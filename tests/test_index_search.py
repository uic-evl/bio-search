import pytest
import lucene
import pandas as pd

from src.index_writer import Indexer
from src.index_reader import Reader


@pytest.fixture
def lucene_vm():
    """ init java virtual machine"""
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])


class TestSearch:
    """ test search """
    def test_search_by_range_dates(self, lucene_vm):
        """ Search by range of dates """
        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        # search between range
        start_date = '2001-05-01'
        end_date = '2001-08-30'
        results = reader.search(terms=None,
                                start_date=start_date,
                                end_date=end_date,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 2
        titles = [x.title for x in results]
        title1 = "Clinical features of culture-proven Mycoplasma pneumoniae " \
                  "infections at King Abdulaziz University Hospital, Jeddah, " \
                  "Saudi Arabia"
        title2 = "Gene expression in epithelial cells in response to pneumovirus infection"
        assert title1 in titles
        assert title2 in titles

    def test_search_for_specific_day(self):
        """ search for documents in an specific date """

        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        start_date = '2000-08-25'
        results = reader.search(terms=None,
                                start_date=start_date,
                                end_date=None,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 1
        titles = [x.title for x in results]
        title = "Surfactant protein-D and pulmonary host defense"
        assert title in titles

    def test_search_by_text_term(self):
        """ search by indexed and parse text term """
        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        term = 'respiratory'
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 4
        titles = [x.title for x in results]
        title = "Role of endothelin-1 in lung disease"
        assert title not in titles

    def test_search_by_text_term2(self):
        """ second test for search by indexed and parse text term """
        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        term = 'infections'
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 2
        titles = [x.title for x in results]
        title1 = "Clinical features of culture-proven Mycoplasma pneumoniae " \
                  "infections at King Abdulaziz University Hospital, Jeddah, " \
                  "Saudi Arabia"
        title2 = "Gene expression in epithelial cells in response to pneumovirus infection"
        assert title1 in titles
        assert title2 in titles

    def test_search_by_multiple_text_terms(self):
        """ Search by multiple keywords. Parser uses OR for each keyword, thus,
            respiratory infections retrieves 4 results although there are
            only two results for infections (based on two previous tests)
        """
        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        term = 'respiratory infections'
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 4
        titles = [x.title for x in results]
        title1 = "Clinical features of culture-proven Mycoplasma pneumoniae " \
                  "infections at King Abdulaziz University Hospital, Jeddah, " \
                  "Saudi Arabia"
        title2 = "Gene expression in epithelial cells in response to pneumovirus infection"
        assert title1 in titles
        assert title2 in titles
        title = "Role of endothelin-1 in lung disease"
        assert title not in titles

    def test_search_by_text_term_in_date_range(self):
        """ Search by 'respiratory' with date range """
        data_filepath = './test_data.csv'
        tmp_index_path = './indexes'

        dataframe = pd.read_csv(data_filepath)
        indexer = Indexer(tmp_index_path, create_mode=True)
        indexer.index_from_dataframe(dataframe)

        reader = Reader(tmp_index_path)
        term = 'respiratory infections'
        start_date = '2000-08-01'
        end_date = '2000-08-30'
        results = reader.search(terms=term,
                                start_date=start_date,
                                end_date=end_date,
                                modalities=None,
                                max_docs=10)
        assert len(results) == 2
        titles = [x.title for x in results]
        title1 = "Nitric oxide: a pro-inflammatory mediator in lung disease?"
        title2 = "Surfactant protein-D and pulmonary host defense"
        assert title1 in titles
        assert title2 in titles
