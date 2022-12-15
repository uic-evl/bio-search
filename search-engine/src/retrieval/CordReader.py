""" Utility class that parses the CORD19 metadata file to provide quick access
to particular properties. Alleviates the need for iterating over the CSV by 
creating intermediate dictionary mappers.
"""

import csv
import json
from pathlib import Path


class CordReader:
    """CORD19 utility class reader"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.metadata_path = self.base_path / "metadata.csv"
        self.full_text_mapping = self.base_path / "corduid_2_fulltext.json"
        self.id2ftpointer = None

        if self.full_text_mapping.exists():
            with open(self.full_text_mapping, "r", encoding="utf-8") as map_file:
                self.id2ftpointer = json.load(map_file)

    def create_id2full_text_mapping(self) -> None:
        """saves a dictionary mapping a cord_uid to the location of the full text"""
        mapping = {}
        with open(self.metadata_path, encoding="utf-8") as meta_file:
            reader = csv.DictReader(meta_file)
            for row in reader:
                cord_uid = row["cord_uid"]
                mapping[cord_uid] = ""

                ft_pointer = row.get("pdf_json_files", None)
                if ft_pointer:
                    mapping[cord_uid] = self._parse_paths(ft_pointer)

        json_object = json.dumps(mapping)
        with open(self.full_text_mapping, "w", encoding="utf-8") as outfile:
            outfile.write(json_object)

    def fetch_full_text(self, corduid: str) -> str:
        """fetch the full text from the metadata file"""
        ft_path = self.id2ftpointer[corduid]

        with open(ft_path, "r", encoding="uft-8") as ft_file:
            full_text_data = json.load(ft_file)
            text_blocks = [el["text"] for el in full_text_data["body_text"]]
            return " ".join(text_blocks)

    def _parse_paths(self, urls: str):
        """some urls contain multiple pointers, if so, get the first one"""
        urls_split = urls.split(";")
        if len(urls_split) > 1:
            return urls_split[0].strip()
        else:
            return urls
