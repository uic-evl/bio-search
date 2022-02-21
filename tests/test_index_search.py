from shutil import rmtree
import pytest
import lucene
import pandas as pd

from src.index_writer import Indexer
from src.index_reader import Reader


@pytest.fixture
def lucene_vm():
    """ Init java virtual machine. Called once on the first test and 
        reused on the rest. Passing fixture to all the test causes an exception.
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])


@pytest.fixture
def temp_index_path():
    """ Indexes the dataframe for all the test cases in TestSearch. Uses 
        pytest fixture to yield the indexes path while the test are in progress.
        Once completed, deletes the indexes.
    """
    index_path = './indexes'
    data_filepath = './test_data.csv'
    dataframe = pd.read_csv(data_filepath)
    indexer = Indexer(index_path, create_mode=True)
    indexer.index_from_dataframe(dataframe)
    yield index_path
    rmtree(index_path)


class TestSearch:
    """ test search """

    # Disable redefinition of fixtures
    # pylint: disable=redefined-outer-name

    def test_search_by_range_dates(self, lucene_vm, temp_index_path):  # pylint: disable=unused-argument
        """ Search by range of dates """
        reader = Reader(temp_index_path)
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

    def test_search_for_specific_day(self, temp_index_path):
        """ search for documents in an specific date """
        reader = Reader(temp_index_path)
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

    def test_search_by_text_term(self, temp_index_path):
        """ search by indexed and parse text term """
        reader = Reader(temp_index_path)
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

    def test_search_by_text_term2(self, temp_index_path):
        """ second test for search by indexed and parse text term """
        reader = Reader(temp_index_path)
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

    def test_search_by_multiple_text_terms(self, temp_index_path):
        """ Search by multiple keywords. Parser uses OR for each keyword, thus,
            respiratory infections retrieves 4 results although there are
            only two results for infections (based on two previous tests)
        """
        reader = Reader(temp_index_path)
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

    def test_search_by_text_term_in_date_range(self, temp_index_path):
        """ Search by 'respiratory' with date range """
        reader = Reader(temp_index_path)
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
