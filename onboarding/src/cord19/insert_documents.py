from document import load_from_cord, insert_documents_to_db, load_from_tinman
from os import listdir
from pathlib import Path
from dotenv import dotenv_values


def insert_documents_from_cord19(config: dict, cord19_metadata_path: str):
    print("inserting documents from the CORD19 collection")
    pdf_location_uic = "cord19-uic"
    pdf_location_udel = "CORD19/batch_udel/PDFs"
    existing_pdfs_uic = {
        x: f"{pdf_location_uic}/{x}/main.pdf" for x in listdir(root / pdf_location_uic)
    }
    existing_pdfs_udel = {
        x[:-4]: f"{pdf_location_udel}/{x}" for x in listdir(root / pdf_location_udel)
    }
    existing_pdfs_uic.update(existing_pdfs_udel)
    documents = load_from_cord(cord19_metadata_path, existing_pdfs_uic)
    insert_documents_to_db(config, documents)


def insert_documents_from_tinman(config: dict, tinman_base_path: str):
    print("inserting documents from the tinman collection")
    documents = load_from_tinman(tinman_base_path)
    insert_documents_to_db(config, documents)


if __name__ == "__main__":
    env_file = "../../.env"
    config = dotenv_values(env_file)
    root = Path("/Users/jtrell2/data/biocuration/")

    # INSERT DOCUMENTS
    # first, CORD19 documents
    metadata_path = root / "cord19_datasets/2022-06-02/metadata.csv"
    insert_documents_from_cord19(config, metadata_path)
    # second, insert the documents used for tinman
    tinman_base_path = root / "tinman"
    insert_documents_from_tinman(config, tinman_base_path)
