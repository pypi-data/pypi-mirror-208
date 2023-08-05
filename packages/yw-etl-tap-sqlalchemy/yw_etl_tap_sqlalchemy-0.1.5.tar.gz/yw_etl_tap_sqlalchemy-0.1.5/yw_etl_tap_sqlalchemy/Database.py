from pathlib import Path
from urllib.parse import urlparse, parse_qs

from impala.dbapi import connect as impala_connect
from sqlalchemy import create_engine, text


class CONN_SCHEME:
    IMPALA_PYODBC = "impala+pyodbc"
    MYSSQL_PYODBC = "mssql+pyodbc"
    SQLITE = "sqlite"


def _get_engine(conn_str: str):
    conn_url = urlparse(conn_str)
    scheme = conn_url.scheme

    # Impala connection via SQLAlchemy
    # see https://github.com/cloudera/impyla/issues/214
    if scheme == CONN_SCHEME.IMPALA_PYODBC:
        qs = parse_qs(conn_url.query)
        auth_mechanism = qs.get('auth_mechanism', [None])[0]
        if auth_mechanism is None:
            raise Exception(
                "impala+pyodbc connection string requires parameter: auth_mechanism, supported value "
                "['LDAP', 'NOSASL', 'PLAIN', 'GSSAPI', 'JWT'] "
                "see https://github.com/cloudera/impyla/blob/master/impala/dbapi.py#L71")

        p = Path(conn_url.path)
        database = None
        if len(p.parts) >= 2:
            database = p.parts[1]

        def conn():
            return impala_connect(
                host=conn_url.hostname, port=conn_url.port,
                database=database, user=conn_url.username, password=conn_url.password,
                auth_mechanism=auth_mechanism
            )

        return create_engine("impala://", creator=conn)
    else:
        return create_engine(conn_str)


class Database:
    def __init__(self, conn_str):
        self.conn_str = conn_str
        self._test_conn()
        self._conn_ctx = None

    def _test_conn(self):
        engine = _get_engine(self.conn_str)
        with engine.connect() as con:
            sql = "select 1" if "oracle" not in self.conn_str else "select 1 AS a from DUAL"
            con.execute(text(sql)).all()

        self.engine = engine

    def __enter__(self):
        self._conn_ctx = self.engine.connect()
        return self._conn_ctx.__enter__()

    def __exit__(self, *args, **kwargs):
        self._conn_ctx.__exit__(*args, **kwargs)
        self._conn_ctx = None
