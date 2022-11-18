import psycopg


def connect(
    host: str, port: int, dbname: str, user: str, password: str
) -> psycopg.Connection:
    """Start a connection to the database"""
    conn_str = (
        f"host={host} port={port} dbname={dbname} user={user} password={password}"
    )
    return psycopg.connect(conn_str)


def simple_select(db_params: dict, query: str) -> list[tuple]:
    """Run a simple select query"""
    try:
        conn = connect(**db_params)
        with conn.cursor() as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return rows
    except Exception as e:
        print(e)
    finally:
        if conn:
            conn.close()
