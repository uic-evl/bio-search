""" Databse entities and utils """

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
from datetime import datetime
import psycopg
from dotenv import dotenv_values


class FigureType(Enum):
    """Figure type in the database"""

    FIGURE = 0
    SUBFIGURE = 1


class FigureStatus(Enum):
    """Figure status in the database
    Imported: The figure was imported from after segmentation
    Verified: Every subfigure has been validated
    """

    IMPORTED = 0
    VERIFIED = 1


class SubFigureStatus(Enum):
    """Subfigure status in database
    Not predicted: The record was just imported from disk
    Predicted: A model estimated the label
    Ground Truth: Someone validated the label
    """

    NOT_PREDICTED = 2
    PREDICTED = 3
    GROUND_TRUTH = 4


@dataclass
class ConnectionParams:
    """Connection params to postgresql database"""

    host: str
    port: int
    dbname: str
    user: str
    password: str
    schema: str

    def conninfo(self):
        """Postgresql connection string"""
        # pylint: disable=line-too-long
        return f"host={self.host} port={self.port} dbname={self.dbname} user={self.user} password={self.password}"


def params_from_env(env_path: str) -> ConnectionParams:
    """Read connection params from .env"""
    config = dotenv_values(env_path)
    return ConnectionParams(
        config["host"],
        config["port"],
        config["dbname"],
        config["user"],
        config["password"],
        config["schema"],
    )


def connect(conn_params: ConnectionParams) -> psycopg.Connection:
    """Establish a database connection"""
    conn_str = f"host={conn_params.host} port={conn_params.port} dbname={conn_params.dbname} user={conn_params.user} password={conn_params.password}"
    connection = psycopg.connect(conn_str)
    connection.autocommit = False
    return connection


@dataclass
class DbDocument:
    """Document in database"""

    title: str
    project: str
    status: str
    import_date: datetime
    abstract: Optional[str] = field(default=None)
    authors: Optional[list[str]] = field(default=None)
    publication_date: Optional[datetime] = field(default=None)
    modalities: Optional[list[str]] = field(default=None)
    pmcid: Optional[str] = field(default=None)
    pubmed_id: Optional[int] = field(default=None)
    journal: Optional[str] = field(default=None)
    repository: Optional[str] = field(default=None)
    cord_uid: Optional[str] = field(default=None)
    license: Optional[str] = field(default=None)
    uri: Optional[str] = field(default=None)
    doi: Optional[str] = field(default=None)
    notes: Optional[str] = field(default=None)

    def to_tuple(self):
        """Return data as tuple to insert in database"""
        return (
            self.title if self.title is not None else None,
            self.authors,
            self.abstract if self.abstract is not None else None,
            self.publication_date,
            self.pmcid,
            self.pubmed_id,
            self.journal if self.journal is not None else None,
            self.repository,
            self.project,
            self.license,
            self.status,
            self.uri,
            self.doi,
            self.notes,
            self.import_date,
        )


@dataclass
class DBFigure:
    """Figure in database"""

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
    page: Optional[int]

    def to_tuple(self):
        """Return data as tuple to insert in database"""
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
            self.page,
        )
