import psycopg


def connect(
    host: str, port: int, dbname: str, user: str, password: str
) -> psycopg.Connection:
    conn_str = (
        f"host={host} port={port} dbname={dbname} user={user} password={password}"
    )
    return psycopg.connect(conn_str)
