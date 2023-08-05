from pathlib import Path

import singer
from singer import CatalogEntry

from yw_etl_tap_sqlalchemy.Database import Database
from yw_etl_tap_sqlalchemy.tapstream.TapStream import TapStream


class CustomQueryTapStream(TapStream):
    def __init__(self, catalog_entry: CatalogEntry, config, state, db: Database, sql_dir: Path):
        super().__init__(catalog_entry, config, state)

        self.db = db

        query_file = self.stream_meta.get('replication-sql-file', None)
        if query_file is None:
            raise Exception(
                f"{self} : replication-sql-file is not set")
        if (query_file_path := Path(query_file)).is_absolute():
            self._query = query_file_path.read_text()
        else:
            self._query = (sql_dir / query_file_path).read_text(encoding='utf8')

    def sync(self):
        singer.write_schema(self.catalog_entry.stream, self.catalog_entry.schema.to_dict(), [])
        with self.db as conn:
            cur = conn.execute(self._query)
            for row in cur:
                record = {k: row[k] for k in row.keys()}
                singer.write_record(self.stream_name, record)
