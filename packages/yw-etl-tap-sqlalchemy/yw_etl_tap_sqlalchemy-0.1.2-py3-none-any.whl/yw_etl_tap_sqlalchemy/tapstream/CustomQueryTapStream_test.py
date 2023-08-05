import contextlib
from unittest import TestCase

import singer
import sqlalchemy

from yw_etl_tap_sqlalchemy.Database import Database
from yw_etl_tap_sqlalchemy.tapstream import get_tap_stream
from yw_etl_tap_sqlalchemy.utils import _TEST_RESOURCE


class TestCustomQueryTapStream(TestCase):
    db_path = (_TEST_RESOURCE / 'test_db.db').absolute()

    @classmethod
    def prepare_db(cls) -> str:
        cls.db_path.unlink(missing_ok=True)
        cls.db_path.touch()
        conn_str = f"sqlite:///{cls.db_path}"

        engine = sqlalchemy.create_engine(conn_str)
        table_name = "test_table"
        with engine.connect() as conn:
            # create table
            ddl = f"""
            create table {table_name}(
                a int,
                b text
            )
            """
            conn.execute(ddl)
            # populate data
            temp_sql = f"insert into {table_name} values(:a, :b)"
            data = [(1, 'A'), (2, 'B'), (3, 'C')]
            for a, b in data:
                conn.execute(temp_sql, {"a": a, "b": b})

        return conn_str

    @classmethod
    def prepare_wd(cls, conn_str):
        """
        :param conn_str:
        :return: config_path, catalog_path, sql_path
        """
        sql_path = _TEST_RESOURCE / 'sql' / 'stream_1.sql'

        config = {
            "connection.conn_string": conn_str,
            "sync.include_streams": ["1"]
        }
        catalog = singer.Catalog.from_dict({
            "streams": [
                {
                    "tap_stream_id": "1",
                    "stream": "stream 1",
                    "schema": {},
                    "metadata": [
                        {
                            "breadcrumb": [],
                            "metadata": {
                                "replication-method": "CUSTOM_QUERY",
                                "replication-sql-file": "stream_1.sql"
                            }
                        }
                    ]
                }
            ]
        })
        stream_sql = "select * from test_table"

        sql_path.parent.mkdir(exist_ok=True)
        with open(sql_path, 'w') as f:
            f.write(stream_sql)

        return config, catalog, sql_path

    def test_sync(self):
        conn_str = self.prepare_db()
        config, catalog, sql_path = self.prepare_wd(conn_str)
        sql_dir = _TEST_RESOURCE / 'sql'
        state = {}

        # redirect stdout to file
        out_file = _TEST_RESOURCE / 'actual_stdout.txt'
        with (
            open(out_file, 'w') as out,
            contextlib.redirect_stdout(out)
        ):
            for stream_id in config['sync.include_streams']:
                catalog_entry = catalog.get_stream(stream_id)
                database = Database(conn_str)
                tap_stream = get_tap_stream(catalog_entry, config, state, database, sql_dir)
                tap_stream.sync()

        exp = (_TEST_RESOURCE / 'expect_stdout.txt').read_text()
        actual = out_file.read_text()
        self.assertEqual(exp, actual)

        out_file.unlink(missing_ok=True)
        self.db_path.unlink(missing_ok=True)
        sql_path.unlink(missing_ok=True)
