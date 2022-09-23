# Search Engine for CORD-19 Collection


http.server 6000 on /mnt


## Web server

```bash
cd src/
export FLASK_APP=app
flask run

```

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
