""" Databse entities and utils """

from dataclasses import dataclass
from dotenv import dotenv_values


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
