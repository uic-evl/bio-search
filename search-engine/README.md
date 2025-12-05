# Search Engine

Sub-project that manages the interaction with Pylucene to index and search over
a document collection with the Cord-19 format. This project uses Lucene 10.

## 1. Development

### Setting up your environment

It is highly recommended to use a development container to work on the search
engine because it simplifies working with Lucene (pylucene). By using the dev
container you will not need to install Lucene in your machine. Follow these steps
to prepare your environment (with VSCode):

1. Add the Docker and the Dev Containers extension
2. Install Docker in your machine (Docker Desktop for Mac works too)
3. Open the `.devcontainer/devcontainer.json` file within this project. You will
   notice in the `mounts` section that we will mount a local folder (~/biosearchdev)
   from your local machine to the `/mnt` directory in the container. These folder
   will help to transfer data back and forth if needed and you can later change it
   as you see fit.
4. For now we will stick with the folder `biosearchdev` so create it in your home
   directory: `mkdir ~/biosearchdev`
5. Press `Ctrl + Shift + p`
6. Select `Dev Containers: Open folder in container...` and press enter
7. Confirm that we will open this folder (`search-engine`)
8. Wait for docker to create the image and start the container. VSCode will open 
   in a new window.
9. Now you are using VSCode from within the container. Any change in the code will
   be reflected in your local machine. The container does not have git so use just 
   make sure that you commit your changes later from your host machine.
10. You can leave the environment by using the button on the bottom left of the IDE
    and choose `Close Remote Connection` or `Reopen locally`.

### Getting familiar with Lucene

The `notebooks` folder has a couple of python notebooks showing common functions
used in this project:

1. 0_pylucene.ipynb: Explores the functions from Pylucene of interest
2. 1_highlight.ipynb: Shows an example of how to index a small collection and search
   the highlighter functions.

Run them by opening the notebook, then on the top right click on `Select Kernel`
and choose `Python 3.14.0`.


## 2. Parquet schema

The input parquet should have the following columns and format:

- doc_id : String. Document database ID.
- source : String. Document repository (e.g., pubmed)
- title : String.
- abstract : String.
- pub_date : String in format YYYY-MM-DD.
- journal : String.
- authors : String separated by ; to represent a list.
- pmcid : String.
- num_figures : Number.
- modalities : String separated by ; to represent a list. Each modality follows a <parent>.<child>.<subchild> format and includes all level of the branch. For instance, `Experimental-Western Blot` includes `exp`, `exp.gel`, and `exp.gel.wes`. This metadata allows to filter images by different levels in the taxonomy.
- url: String. Document DOI.
- captions: List of objects in the format `[{'figure_id': NUMBER}, 'text': STRING}, ...]`
- otherid: String. Another document ID.

## 3. Indexing

Index a collection of documents in the parquet file by providing the `INPUT_PATH` to the
parquet file and an `OUTPUT_PATH` for the folder location of the Lucene indexes. To index
full text, extend the `index.py` function to use a class that serves these information
based on a key in the parquet file columns. `src.CordReader` provides an example
for fetching the full text using the metadata.csv and .json files provided with the
CORD-19 dataset.

### 3.1 Indexing with Docker

Using Docker is the easiest way to index a parquet file because it provisions the PyLucene installation. You need to define a name for the docker image (`IMAGE_NAME`) and mount a path that contains the `INPUT_PATH` and `OUTPUT_PATH`. For this example, `PROJECT_PATH` contains both locations and when mounted, we provide the relative paths of `INPUT_PATH` and `OUTPUT_PATH` to `PROJECT_PATH` (`RELATIVE_INPUT_PATH` and `RELATIVE_OUTPUT_PATH`).

```bash
# build image
docker build -t IMAGE_NAME:latest .
# execute indexing
docker run --rm -v PROJECT_PATH:/mnt IMAGE_NAME:latest RELATIVE_INPUT_PATH RELATIVE_OUTPUT_PATH
```

### 3.2 Using Python script

Make sure that you have PyLucene installed for your local Python environment. For example,
check the `developing` section below.

```bash
python src/index.py INPUT_PATH OUTPUT_PATH
```

### 2.3 Indexing the CORD-19 collection

Add the `METADATA_PATH` to the folder location to the metadata.csv and document_parses folder, which you obtain from unzipping the CORD-19 dataset. If you are running Docker, you can mount a new volume and make `--c` point to the corresponding path.

```bash
python src/index.py INPUT_PATH OUTPUT_PATH --c METADATA_PATH
```

## 4. Lucene Schema

```python
'cord_uid': StringField.TYPE_STORED,
'source_x': StringField.TYPE_STORED,
'title': TextField.TYPE_STORED,
'abstract': TextField.TYPE_STORED,
'publish_time': LongPoint,
'journal': StringField.TYPE_STORED,
'authors': TextField.TYPE_STORED,
'url': StringField.TYPE_STORED,
'pmcid': StringField.TYPE_STORED,
'modalities': StringField.TYPE_STORED # separated by ;
```


## 5. Tests

`test_data.csv` contains 5 entries from the CORD-19 metadata file. For these
tests, we added the `modalities` column with fake data to test the Indexer and
Reader components.

```python
  # for all tests
  pytest -q

  # for coverage report
  pytest --cov=str tests/
```
