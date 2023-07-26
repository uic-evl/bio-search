# Content Onboarding

Library to import PMC documents from CORD19 into the image+text search system.

## 2. Search API

The front-end interface requires two API services: search over the indexes and
retrieve document information. We expose those services as a Flask web server
in `biosearch_core/app.py`. Because the search over indexes uses PyLucene and
PyLucene is not pip installable, we use a Docker container to deploy this component.
The Dockerfile is avaiable at: `dockerfiles/search-api`.

### 2.1. Environmental variables

- INDEX_PATH: Path to the Lucene indexes, usually mounted to /mnt so this path will be /mnt/indexes or similar
- FLASK_ROOT: URL endpoint. For instances, '' for local deployments using hostname:port, and name-based when using a proxy (e.g., server/search-api)
- DBNAME: database name
- DBUSER: database user
- DBPASSWORD: database password
- DBPORT: database port
- DBHOST: database host
- SCHEMA: database content schema (e.g., gxd)

### 2.2. Deployment

Deploy the Flask application in a Docker container:

1. Create a `.env` file with the environmental variables in the folder with the Dockerfile.
2. Build the image
3. Run the container, the app starts when the container runs.

```bash
docker build --t IMAGE_NAME .
docker run -ti -d --rm -p LOCAL_PORT:5000 -v PARENT_TO_INDEX_FOLDER_PATH:/mnt IMAGE_NAME:VERSION
```

<details>
  <summary>Why interactive dettach</summary>
  Without `-ti -d`, running the docker container starts Flask and then you cannot
  detach from the window using control P + Q. More details https://stackoverflow.com/questions/19688314/how-do-you-attach-and-detach-from-dockers-process.   
</details>

### TODO:

The application can use a web server like gunicorn, but we would need to update
how to send the environmental variables.

## Pipeline

At high level, every PDF document is stored in a folder with all other artifacts.
The location of this content in the project structure determines its status in
the pipeline:

1. New content shows up in the `to_extract` folder.
2. The extraction module moves the folder to `to_segment`.
3. Next, the segmentation module moves the folder to `to_import`.
4. The import module insert the data to the document and figures table, and moves the folder to `to_predict`.
5. The prediction module updates the label tables with the predictions per classifier and moves the folde to `data`
6. The indexer updates the search system indexes.

### Project structure

```
projects_dir/
  project_name/
    indexes/    # Lucene indexes
    data/       # content available for indexing
    to_predict/ # folders that need modality predictions
    to_import/  # folders to import to db
    to_segment/ # folders after extraction
    to_extract/ # newly add folders
    xpdf/       # stores PDF content as images
    logs/
```

dev
