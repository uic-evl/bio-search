from dataclasses import dataclass
from typing import Optional
from utils import connect
import numpy as np
from pathlib import Path
import pandas as pd

STATUS_LABELED = 0
STATUS_UNLABELED = 1
STATUS_LABELED_EXTERNALLY = 2

TYPE_FIGURE = 0
TYPE_SUBFIGURE = 1


@dataclass
class Figure:
    status: str
    uri: str
    width: float
    height: float
    type: int
    source: str
    id: Optional[int]
    name: Optional[str]
    caption: Optional[str]
    num_panes: Optional[int]
    doc_id: Optional[int]
    parent_id: Optional[int]
    coordinates: Optional[list[float]]
    last_update_by: Optional[str]
    owner: Optional[str]
    migration_key: Optional[str]
    notes: Optional[str]
    labels: Optional[list[str]]

    def to_tuple(self):
        return (
            self.name,
            self.caption,
            self.num_panes,
            self.type,
            self.doc_id,
            self.status,
            self.uri,
            self.parent_id,
            self.width,
            self.height,
            self.coordinates,
            self.last_update_by,
            self.owner,
            self.migration_key,
            self.notes,
            self.labels,
            self.source,
        )


@dataclass
class Observation:
    id: int
    figure_id: int
    needs_cropping: bool
    is_compound: bool
    is_overcropped: bool
    is_missing_subfigures: bool
    is_close_up: bool
    is_missing_subfigures: bool
    is_missing_panels: bool
    is_overfragmented: bool
    num_subpanes: int
    composition: Optional[str]

    def to_tuple(self):
        return (
            self.needs_cropping,
            self.is_compound,
            self.is_overcropped,
            self.is_missing_subfigures,
            self.is_close_up,
            self.num_subpanes,
            self.is_missing_panels,
            self.figure_id,
            self.is_overfragmented,
            self.composition,
        )


@dataclass
class Label:
    figure_id: int
    classifier: str
    label: Optional[str]
    prediction: Optional[str]
    features: Optional[np.ndarray]
    pred_probs: Optional[np.ndarray]
    margin_sample: Optional[float]
    entropy: Optional[float]
    split_set: str

    def to_tuple(self):
        return (
            self.figure_id,
            self.classifier,
            self.label,
            self.prediction,
            self.features.tolist(),
            self.pred_probs.tolist(),
            self.margin_sample,
            self.entropy,
            self.split_set,
        )


def insert_figures(db_params: dict, figures: list[Figure]):
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            with cur.copy(
                "COPY dev.figures (name,caption,num_panes,fig_type,doc_id,status,uri,parent_id,width,height,coordinates,last_update_by,owner,migration_key,notes,labels,source) FROM STDIN"
            ) as copy:
                for f in figures:
                    copy.write_row(f.to_tuple())
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def get_full_labels(df) -> dict[str, str]:
    labels = {}
    for _, el in df.iterrows():
        labels[el.img_path] = el.label
    return labels


def load_images_from_external_sources(df, full_labels):
    """
    Get the images that belong to any dataset that is not cord19 or tinman
    full_labels: reverse lookup dictionary that given a path returns the most
                 detailed labeled encountered for an image. This is needed as
                 bi-lava stored partial labels per parquet file
    """
    figures = []

    for _, el in df.iterrows():
        # df_all has the more detailed labels
        label = full_labels[el.img_path]
        figure = Figure(
            id=None,
            status=STATUS_LABELED_EXTERNALLY,
            uri=el.img_path,
            width=el.width,
            height=el.height,
            type=TYPE_SUBFIGURE,
            name=el.name,
            caption=None if el.caption == "" else el.caption,
            num_panes=1,
            doc_id=None,
            parent_id=None,
            coordinates=None,
            last_update_by=None,
            owner=None,
            migration_key=None,
            notes=None,
            labels=[label],
            source=el.source,
        )
        figures.append(figure)
    return figures


def build_pmc_to_id_doc_dic(db_params) -> dict[str, str]:
    """Get a dictionary [pmcid, doc_id] to match figures to their corresponding
    source documents"""
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            cur.execute("select id, pmcid from dev.documents where pmcid != ''")
            rows = cur.fetchall()
            return {r[1]: r[0] for r in rows}
    except Exception as e:
        print(e)
        raise Exception(e)
    finally:
        conn.close()


def is_figure(splits: int) -> int:
    """
    the case for 3 splits is very weird and may be related to some
    errors while exporting the data. It also seems to be repeated data.
    """
    if splits == 3:
        return TYPE_FIGURE
    if splits == 4:
        return TYPE_FIGURE
    elif splits == 5:
        return TYPE_SUBFIGURE
    else:
        return -1


def calc_img_path_length(img_path: str) -> int:
    # supplementary material processed have an additional level to the structure
    splits = img_path.split("/")
    return len(splits) if "supplementary" not in splits else len(splits) - 1


def get_parent_image(img_path: str, type: int) -> str:
    if type == TYPE_FIGURE:
        return None
    else:
        if "figsplit" in img_path:
            return f"{str(Path(img_path).parent)}.jpg".replace("figsplit_", "")
        else:
            return f"{str(Path(img_path).parent)}.jpg"


def extract_pmcid(img_path):
    els = img_path.split("/")
    return els[1]


def load_figures_from_cord19(df, pmc2id_dict: dict[str, str]):
    figures = []
    for _, el in df.iterrows():
        pmcid = extract_pmcid(el.img_path)
        doc_id = pmc2id_dict.get(pmcid, None)

        if doc_id is None:
            print(el.img_path)

        figure = Figure(
            id=None,
            status=STATUS_UNLABELED,
            uri=el.img_path,
            width=el.width,
            height=el.height,
            type=el.type,
            name=el.name,
            caption=None if el.caption == "" else el.caption,
            num_panes=1,
            doc_id=doc_id,
            parent_id=el.parent_id,
            coordinates=el.coordinates,
            last_update_by=None,
            owner=None,
            migration_key=None,
            notes=None,
            labels=None,  # all this data is unlabeled,
            source=el.source,
        )
        figures.append(figure)
    return figures


def get_map_fig_uri_2_db_id(db_params: dict) -> dict[str, int]:
    """
    Query the database for the insert figures and create a dictionary that
    matches the figure path to the database id. We can just this match to
    populate the figure id for the labels table.
    """
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            cur.execute("select id, uri from dev.figures")
            rows = cur.fetchall()
            return {r[1]: r[0] for r in rows}
    except Exception as e:
        print(e)
        raise Exception(e)
    finally:
        conn.close()


def get_coordinate_mapping(df, base_path: Path):
    # match coordinates to subfigure img_path
    subfigure_paths = list(set([f"{Path(x).parent}" for x in df.img_path]))

    img_path_2_coordinates = {}
    fails = []
    for p in subfigure_paths:
        filename = f"{Path(p).name}.jpg.txt"
        try:
            with open(base_path / p / filename, "r") as f:
                # ignore first and second lines
                lines = f.readlines()[2:]
                for idx, line in enumerate(lines):
                    line = line.replace("    ", " ").replace("\n", "").strip()
                    line = line.split(" ")
                    line = [float(x) for x in line if x != ""]
                    name = f"{p}/{str(idx+1).zfill(3)}.jpg"
                    img_path_2_coordinates[name] = line
        except FileNotFoundError as error:
            fails.append(p)
    return img_path_2_coordinates


def build_tinman_doc_mapping(db_params) -> dict[str, str]:
    """Use the root folder as the key to link documents and images"""
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            cur.execute("select id, uri from dev.documents where uri like '%tinman%'")
            rows = cur.fetchall()
            return {r[1].split("/")[1]: r[0] for r in rows}
    except Exception as e:
        print(e)
        raise Exception(e)
    finally:
        conn.close()


def load_images_from_tinman(df, full_labels: dict[str, str]):

    figures = []
    for _, el in df.iterrows():
        label = full_labels.get(el.img_path, None)
        label = [label] if label is not None else None

        if el.doc_id is None:
            print(el.img_path)

        figure = Figure(
            id=None,
            status=STATUS_UNLABELED,
            uri=el.img_path,
            width=el.width,
            height=el.height,
            type=el.type,
            name=el.name,
            caption=None if el.caption == "" else el.caption,
            num_panes=1,
            doc_id=el.doc_id,
            parent_id=el.parent_id,
            coordinates=el.coordinates,
            last_update_by=None,
            owner=None,
            migration_key=None,
            notes=None,
            labels=label,
            source=el.source,
        )
        figures.append(figure)
    return figures


def insert_labels_per_classifier(db_params: dict, labels: list[Label]):
  try:
    conn = connect(**db_params)
    with conn.cursor() as cur:
      with cur.copy("COPY dev.labels_cord19 (figure_id,classifier,label,prediction,features,pred_probs,margin_sample,entropy,split_set) FROM STDIN") as copy:
        for l in labels:
          copy.write_row(l.to_tuple())
    conn.commit()
  except Exception as e:
    print(e)
    raise Exception(e)
  finally:
    conn.close()  

def insert_labels(db_params: dict, parquet_files: list[Path]):
  uri2id = get_map_fig_uri_2_db_id(db_params)

  for parquet_file in parquet_files:
    classifier = parquet_file.name.split('_')[1]
    print(f"processing {classifier}")
    df = pd.read_parquet(parquet_file)

    if df.shape[0] > 0:
      df = df.replace({np.nan: None})
      df["figure_id"] = df.apply(lambda x: uri2id[x.img_path], axis=1)

      if 'en_metric' not in df.columns:
        df['en_metric'] = None
      if 'ms_metric' not in df.columns:
        df['ms_metric'] = None
      
      labels = []
      for idx, el in df.iterrows():
        label = Label(classifier=classifier,
                      label=el.label,
                      features=el.features,
                      entropy=el.en_metric,
                      figure_id=el.figure_id,
                      margin_sample=el.ms_metric,
                      pred_probs=el.pred_probs,
                      prediction=el.prediction,
                      split_set=el.split_set)
        labels.append(label)
      print(f"inserting labels for {classifier} {len(labels)} rows")
      insert_labels_per_classifier(db_params, labels)
    else:
      print(f"Nothing to insert for {classifier}")