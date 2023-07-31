# Search Engine

Utility functions to interact with PyLucene, including indexing new content from
a parquet file and searching over the indexed content.

## 1. Parquet schema

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

## 2. Indexing

Index a collection of documents in the parquet file by providing the `INPUT_PATH` to the
parquet file and an `OUTPUT_PATH` for the folder location of the Lucene indexes. To index
full text, extend the `index.py` function to use a class that serves these information
based on a key in the parquet file columns. `src.CordReader` provides an example
for fetching the full text using the metadata.csv and .json files provided with the
CORD-19 dataset.

### 2.1 Indexing with Docker

Using Docker is the easiest way to index a parquet file because it provisions the PyLucene installation. You need to define a name for the docker image (`IMAGE_NAME`) and mount a path that contains the `INPUT_PATH` and `OUTPUT_PATH`. For this example, `PROJECT_PATH` contains both locations and when mounted, we provide the relative paths of `INPUT_PATH` and `OUTPUT_PATH` to `PROJECT_PATH` (`RELATIVE_INPUT_PATH` and `RELATIVE_OUTPUT_PATH`).

```bash
# build image
docker build -t IMAGE_NAME:latest .
# execute indexing
docker run --rm -v PROJECT_PATH:/mnt IMAGE_NAME:latest RELATIVE_INPUT_PATH RELATIVE_OUTPUT_PATH
```

### 2.2 Using Python script

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

## 3. Lucene Schema

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

## 4. Development

Installing PyLucene on a local environment is not an easy process, but you can follow that route and use that Python environment for development. An easier alternative is to open this project in a container environment within VSCode. The Dockerfile in `.devcontainer` has the configuration for loading a Python developing environment with all the required libraries. Follow the next steps to use this container environment:

1. Open `.devcontainer/devcontainer.json` and decide if you need to mount a local disk for developing. If so, modify the `mounts` accordingly. While VSCode can open your project folder in the container by default, any other local folder needs to be mapped.
2. Press `Ctrl + Shift + p` and select `Dev Containers: Open folder in container...`, then select the search-engine folder.
3. You can leave the container environment using the button on the bottom left of the IDE.

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
