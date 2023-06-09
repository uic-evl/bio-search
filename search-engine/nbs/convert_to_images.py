from os import listdir, makedirs, system
from pathlib import Path

docs_path = "/media/cumulus/biosearch/cord19/to_predict"
output_folder = "/media/cumulus/curation_data/cord19-pdf-images"

base_path = Path(docs_path)
output_path = Path(output_folder)
folders = listdir(base_path)

for folder in folders:
    documents = [x for x in listdir(base_path / folder) if x.endswith(".pdf")]

    doc_path = base_path / folder / documents[0]
    filename = folder

    target_path = output_path / filename
    makedirs(target_path, exist_ok=True)

    t = f"{target_path}/{filename}"
    x = system(f"pdftopng -r 150 {str(doc_path)} {t}")
