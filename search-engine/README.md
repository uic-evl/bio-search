# Search Engine for CORD-19 Collection

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
