# Content Onboarding

Library to import PMC documents from CORD19 into the image+text search system.

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
