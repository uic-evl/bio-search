"""
  Testing the Reader component based on a set of 5 documents in 
  test_data.csv. All fields in the CSV except for the modalities come from
  some samples of the CORD-19 metadata file.
"""
from shutil import rmtree
import pytest
import lucene
import pandas as pd

from src.index_writer import Indexer
from src.index_reader import Reader, strdate2long


@pytest.fixture
def lucene_vm():
    """ Init java virtual machine. Called once on the first test and 
        reused on the rest. Passing fixture to all the test causes an exception.
    """
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])  # pylint: disable=no-member


@pytest.fixture
def temp_index_path():
    """ Indexes the dataframe for all the test cases in TestSearch. Uses 
        pytest fixture to yield the indexes path while the test are in progress.
        Once completed, deletes the indexes.
    """
    index_path = './tests/indexes'
    data_filepath = './tests/test_data.csv'
    dataframe = pd.read_csv(data_filepath)
    indexer = Indexer(index_path, create_mode=True)
    indexer.index_from_dataframe(dataframe)
    yield index_path
    rmtree(index_path)


# pylint: disable=no-self-use
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

    def test_search_by_one_modality(self, temp_index_path):
        """ search by modality key terms """
        reader = Reader(temp_index_path)
        modalities = ["gra.his"]
        results = reader.search(terms=None,
                                start_date=None,
                                end_date=None,
                                modalities=modalities,
                                max_docs=10)
        assert len(results) == 2
        titles = [x.title for x in results]
        title1 = "Nitric oxide: a pro-inflammatory mediator in lung disease?"
        title2 = "Role of endothelin-1 in lung disease"
        assert title1 in titles
        assert title2 in titles

    def test_search_by_two_modalities(self, temp_index_path):
        """ search by modality key terms """
        reader = Reader(temp_index_path)
        modalities = ["gra.his", "gra.lin"]
        results = reader.search(terms=None,
                                start_date=None,
                                end_date=None,
                                modalities=modalities,
                                max_docs=10)
        assert len(results) == 2
        titles = [x.title for x in results]
        title1 = "Nitric oxide: a pro-inflammatory mediator in lung disease?"
        title2 = "Role of endothelin-1 in lung disease"
        assert title1 in titles
        assert title2 in titles

    def test_search_by_two_modalities_and_term(self, temp_index_path):
        """ search by modality key terms """
        reader = Reader(temp_index_path)
        term = "nitric"
        modalities = ["gra.his", "gra.lin"]
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=modalities,
                                max_docs=10)
        assert len(results) == 1
        titles = [x.title for x in results]
        title1 = "Nitric oxide: a pro-inflammatory mediator in lung disease?"
        assert title1 in titles

    def test_search_only_documents_with_modalities(self, temp_index_path):
        """ filter collection to only documents with a string in the
            modality field """
        reader = Reader(temp_index_path)
        results = reader.search(terms=None,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                only_with_images=True,
                                max_docs=10)
        assert len(results) == 4
        titles = [x.title for x in results]
        title1 = "Surfactant protein-D and pulmonary host defense"
        assert title1 not in titles

    def test_search_results_have_complete_fields_with_modalities(
            self, temp_index_path):
        """ check that results have fields properly filled when the results 
            does contain modalities"""
        reader = Reader(temp_index_path)
        term = "pneumoniae"
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                only_with_images=False,
                                max_docs=10)
        assert len(results) == 1
        document = results[0]

        title = "Clinical features of culture-proven Mycoplasma pneumoniae " \
                "infections at King Abdulaziz University Hospital, Jeddah, " \
                "Saudi Arabia"
        assert document.title == title
        assert not document.abstract is False
        assert not document.publish_date is False
        assert len(document.modalities) > 0

    def test_search_results_have_complete_fields_without_modalities(
            self, temp_index_path):
        """ check that results have fields properly filled when the results 
            does NOT contain modalities"""
        reader = Reader(temp_index_path)
        term = "surfactant"
        results = reader.search(terms=term,
                                start_date=None,
                                end_date=None,
                                modalities=None,
                                only_with_images=False,
                                max_docs=10)
        assert len(results) == 1
        document = results[0]

        title = "Surfactant protein-D and pulmonary host defense"
        assert document.title == title
        assert not document.abstract is False
        assert not document.publish_date is False
        assert len(document.modalities) == 0


class TestSearchUtils:
    """ Test utils used in Reader"""
    def test_strdate2long(self):
        """ transforms string date Y-m-d to int date"""
        str_date = '2022-01-01'
        int_date = strdate2long(str_date)
        assert int_date == 20220101
