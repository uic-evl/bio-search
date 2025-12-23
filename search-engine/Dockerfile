# Image for processing parquet file to create Lucene indexes
# Run as:
#   docker build -t pylucene-index:latest .
#   docker run --rm -v /local/project/path:/mnt pylucene-index:latest /mnt/path/to/parquet /mnt/path/to/index/folder

FROM coady/pylucene:10.0
RUN /usr/local/bin/python -m pip install --upgrade pip \
  && pip install "git+https://github.com/uic-evl/bio-search.git@fix/lucene10#subdirectory=search-engine"
ENTRYPOINT [ "parquet2lucene" ]