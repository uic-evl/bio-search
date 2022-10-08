# Search Engine for CORD-19 Collection

Index data in a parquet file and provide a Flask web server to search over 
that collection.

Now I'm converting to parquet from jupyter but I need a script to do this

## 1. Schema
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

## 2. Index a collection

```python
python index.py --input_path XXXX --output_path YYYY
# e.g.
python src/index.py --input_path sample_data/gxd.parquet --output_path /tmp/gxd
```

## 3. Search web server
### Environmental variables
```
INDEX_PATH = Path to indexes to use for searches, e.g. /tmp/gxd
DATA_PATH = Path to JSON metadata, e.g. ./sample_data/gxd_dict.json
FLASK_ROOT = prefix for API call, e.g., /api
```

### Start Flask
```bash
cd src/
export FLASK_APP=app
flask run
```

http.server 6000 on /mnt


## Tests

`test_data.csv` contains 5 entries from the CORD-19 metadata file. For these
tests, we added the `modalities` column with fake data to test the Indexer and
Reader components.

```python
  # for all tests
  pytest -q

  # for coverage report
  pytest --cov=str tests/
```
