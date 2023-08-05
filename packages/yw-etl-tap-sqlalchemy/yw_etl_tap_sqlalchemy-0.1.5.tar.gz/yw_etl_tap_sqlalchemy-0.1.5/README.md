# tap-sqlalchemy

# Roadmap

### Supported RDBMS

- [x] SQLite, see [SQLite with SQLAlchemy](https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#connect-strings)
- [x] SQL Server,
  see [PyODBC with SQLAlchemy](https://docs.sqlalchemy.org/en/14/dialects/mssql.html#module-sqlalchemy.dialects.mssql.pyodbc)
  > Driver query in connection string:
  > `"mssql+pyodbc://scott:tiger@myhost:port/databasename?driver=ODBC+Driver+17+for+SQL+Server"`
  > https://docs.sqlalchemy.org/en/14/dialects/mssql.html#hostname-connections
- [x] Impala
  > Impala connection string is not natively supported by SQLAlchemy, but
  tap-sqlalchemy provides a familiar connection string format as that of SQLite or SQL Server, and the
  connection capability is supported by [impyla](https://github.com/cloudera/impyla)
  >
  > Example:
  > Impala "connection.conn_string" format:
  >
  > impala+pyodbc://[username][:][password][@]host:port[/default_db]?auth_mechanism=LDAP
  >
  > - auth_mechanism is required, and supports only one value: LDAP
  > - <host> and <port> are required

# Guide

### Tap Installation & Quick Start

1. Create a python virtual environment
2. install tap-sqlalchemy, `pip install yw-etl-tap-sqlalchemy`
3. invoke tap

```shell
$ <venv-bin>/tap-sqlalchemy -c '<config-json>' --catalog '<catalog-json>'
```

### Tap Configuration

Tap Configuration is a JSON document containing entries that will impact the behaviors of data extraction work load.

```json5
{
  // mandatory
  "connection.conn_string": "<SQLAlchemy compatible connection string>",
  // mandatory
  "sync.include_streams": [
    "<tap_stream_id>",
    /* refer to a stream described in Catalog*/
  ],
  // optional
  "sync.working_directory": "..."
}
```

* see SQLAlchemy: [Database URLs](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)
* see [Working Directory](https://github.com/YiwenData/tap-sqlalchemy/issues/2)

### Tap Catalog

Tap Catalog is a JSON document of one object containing definitions of data stream.

```json5
{
  "streams": [
    {
      // mandatory, unique identifier, used in [sync.include_streams] of Tap Configuration
      "tap_stream_id": "...",
      // mandatory, human-friendly identifier, possible to have duplicates inside on Catalog Document
      "stream": "...",
      // mandatory
      // JSON Schema Object describing the shape of this data stream,
      // used for data verification
      // 
      // Empty Object means that schema check will be skipped
      "schema": {},
      // mandatory
      // a list of metadata entries about the whole stream or about one field
      "metadata": [
        {
          // mandatory
          // breadcrumb points to a field to which this metadata entry applies.
          // an array of string, like '["a", "b", "c"]', that is evaluated against this stream's JSON Schema document
          // 
          // Empty List means this is the metadata about the whole stream
          "breadcrumb": [],
          // mandatory
          // specific meta data entry, key value pair
          "metadata": {
            // Two special Keys that are of special interests
            // for SQL-based replication
            "replication-method": "CUSTOM_QUERY",
            // relative path is resolved against
            // <working-directory/sql
            // absolute path is treated as it is
            "replication-sql-file": "query.sql"
          }
        }
      ]
    }
  ]
}
```

* see [JSON Schema](http://json-schema.org/)

# Developer Guide

The idea behind `tap-sqlalchemy` is rather simple: execute SQL query and emit each row to stdout in JSON format.

## Message Format

The emitted message format follows the [Singer Specification](https://github.com/singer-io/getting-started). Current
implementation will emit only `SCHEMA` and `RECORD` message.

## Add new RDBMS support

[SQLAlchemy](https://www.sqlalchemy.org/) is an abstraction layer over various types of Relational Databases (or storage
systems that speak in SQL). It provides a unified SQL execution entrypoint and a unified query return structure.

Out of the box, SQLAlchemy provides working guides for mainstream RDBMS,
including [PostgreSQL](https://docs.sqlalchemy.org/en/14/dialects/postgresql.html)
, [MySQL](https://docs.sqlalchemy.org/en/14/dialects/mysql.html)
, [SQLite](https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#connect-strings)
, [Oracle](https://docs.sqlalchemy.org/en/14/dialects/oracle.html)
and [SQL Server](https://docs.sqlalchemy.org/en/14/dialects/mssql.html). In most cases, a RDBMS specific driver is
required for SQLAlchemy to talks to a RDBMS, but protocol like ODBC and its implementation in
python, [pyODBC](https://pypi.org/project/pyodbc/), can be used for multiple RDBMS.

For more exotic database technologies, like impala or clickhouse, 3rd party adaptor or driver is required. Take Impala
as an example. Impala provides its own driver [implementation in python](https://github.com/cloudera/impyla), however it
is not directly usable by SQLAlchemy,
see [post](https://stackoverflow.com/questions/39582842/impala-connection-via-sqlalchemy). In `Database.py#_get_engine`
, impala connection is treated specially to be compatible with SQAlchemy's `_engine.Engine` interface.

To add support for a new Database system:

1. find its driver implementation in python, it may be built on top of a general protocol,
   like [impyla](https://github.com/cloudera/impyla) over ODBC or a community-maintained SQLAlchemy adaptor,
   like [clickhouse-sqlalchemy](https://pypi.org/project/clickhouse-sqlalchemy/)
2. devise a connection string format that has similar structure as other db (easier to remember) and can express
   special configuration entries for picked database, a common solution is to use URL and query terms.
3. augment method `Database.py#_get_engine` to parse connection string into a connection object and adapt the connection
   object to be compatible with SQAlchemy's `_engine.Engine` interface.
4. at this point, you can issue SQL to new database system in the same fashion as other RDBMS 
