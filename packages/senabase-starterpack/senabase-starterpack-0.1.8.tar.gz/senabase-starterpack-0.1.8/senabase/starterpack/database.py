import psycopg2
from psycopg2.extras import RealDictCursor


class PostgreSQLHandler:

    def __init__(self, host: str, port: int, dbname: str, usrid: str, pwd: str):
        self.configure(host, port, dbname, usrid, pwd)

    def __init__(self):
        self.pg_conn_str: str = ''

    def configure(self, host: str, port: int, dbname: str, usrid: str, pwd: str) -> None:
        """
        Configure postgresql connection string
        :param host: host
        :param port: port
        :param dbname: dbname
        :param usrid: usrid
        :param pwd: password
        :return: None
        """
        self.pg_conn_str = f"host='{host}' port={port} dbname='{dbname}' user={usrid} password={pwd}"

    def get(self, q: str):
        """
        Execute query
        :param q: query
        :return: Result list
        """
        with psycopg2.connect(self.pg_conn_str) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(q)
                rs = cur.fetchall()
            return rs

    def set(self, stmt: str) -> None:
        """
        Execute statement
        :param stmt: statement
        :return: None
        """
        with psycopg2.connect(self.pg_conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(stmt)
