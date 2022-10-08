import psycopg
import csv
from document import Cord19Document
from datetime import datetime
from os import listdir
from pathlib import Path
from dotenv import dotenv_values


def connect(host: str, port: int, dbname: str, user: str, password: str) -> psycopg.Connection:
  conn_str = f"host={host} port={port} dbname={dbname} user={user} password={password}"
  return psycopg.connect(conn_str)


def load_from_cord(metadata_path: Path, pdf_paths: dict[str, str]) -> list[Cord19Document]:
  documents = []

  with open(metadata_path) as f_in:
    reader = csv.DictReader(f_in)

    for row in reader:
      # publish time can be empty or be a YYYY-MM-DD or YYYY
      if len(row['publish_time']) == 0:
        publication_date = None
      elif len(row['publish_time']) == 4:
        publication_date = datetime(int(row['publish_time']), 1, 1)
      else:
        publication_date = datetime.strptime(row['publish_time'], "%Y-%m-%d")

      # check if we have a local copy of the PDF somewhere
      uri = None
      # uic preprocessing used pmcid for folders names
      if row['pmcid'] in pdf_paths:
        uri = pdf_paths[row['pmcid']]
      elif row['cord_uid'] in pdf_paths:
        uri = pdf_paths[row['cord_uid']]

      # pubmed_id should be an integer value
      pubmed_id = int(row['pubmed_id']) if row['pubmed_id'].isdecimal() else None

      # some values have NUL characters
      authors = row['authors'].split('; ')
      if len(authors[0]) == 0:
        authors = None
      else:
        for author in authors:
          author = author.replace("\x00", '')

      document = Cord19Document(title=row['title'],
                              abstract=row['abstract'],
                              authors=authors,
                              modalities=None,
                              publication_date=publication_date,
                              pmcid=row['pmcid'],
                              pubmed_id=pubmed_id,
                              license=row['license'],
                              journal=row['journal'],
                              doi=row['doi'],
                              cord_uid=row['cord_uid'],
                              repository=row['source_x'],
                              uri=uri,
                              status='IMPORTED',
                              project='cord19',
                              notes=None)
      documents.append(document)
    return documents


def insert_documents_to_db(db_params: dict, documents: list[Cord19Document]):
  try:
    conn = connect(**db_params)
    with conn.cursor() as cur:
      with cur.copy("COPY dev.documents (title, authors, abstract, publication_date, pmcid, pubmed_id, journal, repository, project, license, status, uri, doi, notes) FROM STDIN") as copy:
        for d in documents:
          copy.write_row(d.to_tuple())
    conn.commit()
  except Exception as e:
    print(e)
  finally:
    conn.close()


if __name__ == "__main__":
  env_file = '../../.env'
  config = dotenv_values(env_file)

  root = Path('/Users/jtrell2/data/biocuration/')
  pdf_location_uic = 'cord19-uic'
  pdf_location_udel = 'CORD19/batch_udel/PDFs'
  metadata_path = '/Users/jtrell2/data/biocuration/cord19_datasets/2022-06-02/metadata.csv'

  existing_pdfs_uic = {x: f"{pdf_location_uic}/{x}/main.pdf" for x in listdir(root / pdf_location_uic)}
  existing_pdfs_udel = {x[:-4]: f"{pdf_location_udel}/{x}" for x in listdir(root / pdf_location_udel)}
  existing_pdfs_uic.update(existing_pdfs_udel)

  documents = load_from_cord(metadata_path, existing_pdfs_uic)
  insert_documents_to_db(config, documents)

