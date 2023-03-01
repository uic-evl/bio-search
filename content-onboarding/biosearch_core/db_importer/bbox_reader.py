""" Utilities for bounding boxes """

from re import findall
from pathlib import Path
from typing import List, Dict, Optional


class BoundingBoxMapper:
    """Helper to read the bounding boxes from disk and loading them to a mapper.
    FigSplit outputs a *.jpg.txt file with the bounding box in [x, y, width, height]
    format for every processed document. This helper reads that data from file
    for preprocessing steps. For input figures, they are stored in this structure:
    some_base_path/
      document1
        3_1/
          3_1.jpg.txt
          001.jpg
          002.jpg
        4_1/
          4_1.jpg.txt
          001.jpg
          002.jpg
    where path for a subfigure is given by /document1/3_1/001.jpg. Therefore,
    the file of interest (e.g., 3_1.jpg.txt) is a sibling, and a line from that
    file corresponds to 001.jpg
    """

    def __init__(self, base_path: Optional[Path] = None):
        self.base_path = base_path
        self.mapping = {}
        self.errors = []

    def _extract_from_txt(self, parent_path, lines: List[str], prefix: str = None):
        mult_factor = 1
        if "*" in lines[0]:
            # avoid the first two lines when the values need scaling
            mult_factor = float(lines[0].strip().split(" ")[0])
            lines = lines[2:]
        for idx, line in enumerate(lines):
            values = findall(r"\d+\.\d+", line)
            values = [mult_factor * float(x) for x in values]
            if prefix is not None:
                key = f"{parent_path}/{prefix}_{str(idx+1).zfill(3)}.jpg"
            else:
                key = f"{parent_path}/{str(idx+1).zfill(3)}.jpg"
            self.mapping[key] = values

    def _extract_from_csv(self, parent_path, lines: List[str], prefix: str = None):
        for idx, line in enumerate(lines):
            values = line.split(",")
            if prefix is not None:
                key = f"{parent_path}/{prefix}_{str(idx+1).zfill(3)}.jpg"
            else:
                key = f"{parent_path}/{str(idx+1).zfill(3)}.jpg"
            self.mapping[key] = values

    def load(self, subfig_paths: List[str], prefix: str = None) -> Dict:
        """Load the bounding boxes from the artifacts created by FigSplit."""
        # bboxes is stored in the parent figure file
        figure_paths = list(set(f"{Path(x).parent}" for x in subfig_paths))

        for parent_path in figure_paths:
            filename = f"{Path(parent_path).name}.jpg.txt"
            filename_aux = f"{Path(parent_path).name}.csv"
            lines = None

            read_from = None
            try:
                if self.base_path:
                    bboxes_path = self.base_path / parent_path / filename
                else:
                    bboxes_path = Path(parent_path) / filename
                with open(bboxes_path, "r", encoding="utf8") as file:
                    lines = file.readlines()
                    read_from = "txt"
            except FileNotFoundError:
                try:
                    if self.base_path:
                        bboxes_path = self.base_path / parent_path / filename_aux
                    else:
                        bboxes_path = Path(parent_path) / filename_aux
                    with open(bboxes_path, "r", encoding="utf8") as file:
                        lines = file.readlines()
                        read_from = "csv"
                except FileNotFoundError:
                    self.errors.append(parent_path)
                    return

            if read_from == "txt":
                self._extract_from_txt(parent_path, lines, prefix=prefix)
            else:
                self._extract_from_csv(parent_path, lines, prefix=prefix)
