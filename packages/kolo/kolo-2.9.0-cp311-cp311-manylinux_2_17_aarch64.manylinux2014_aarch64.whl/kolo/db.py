from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, MutableMapping, Tuple

from .config import create_kolo_directory


@contextmanager
def db_cursor(db_path, wal_mode=True):
    """
    Wrap sqlite's cursor for use as a context manager

    Commits all changes if no exception is raised.
    Always closes the cursor/connection after the context manager exits.
    """
    if wal_mode:
        connection = sqlite3.connect(str(db_path), isolation_level=None)
        connection.execute("pragma journal_mode=wal")
    else:
        connection = sqlite3.connect(str(db_path))  # pragma: no cover
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    finally:
        cursor.close()
        connection.close()


def get_db_path() -> Path:
    return create_kolo_directory() / "db.sqlite3"


def create_invocations_table(cursor) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS invocations (
        id text PRIMARY KEY NOT NULL,
        created_at TEXT DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')) NOT NULL,
        data text NOT NULL
    );
    """
    create_timestamp_index_query = """
        CREATE INDEX IF NOT EXISTS
        idx_invocations_created_at
        ON invocations (created_at);
        """

    cursor.execute(create_table_query)
    cursor.execute(create_timestamp_index_query)


def setup_db(config: MutableMapping[str, Any] | None = None) -> Path:
    if config is None:
        config = {}
    db_path = get_db_path()

    wal_mode = config.get("wal_mode", True)

    with db_cursor(db_path, wal_mode) as cursor:
        create_invocations_table(cursor)

    return db_path


def save_invocation_in_sqlite(
    db_path: Path,
    trace_id: str,
    json_string: str,
    wal_mode: bool = True,
    ignore_errors: bool = True,
    created_at: datetime | None = None,
) -> None:
    ignore = " OR IGNORE" if ignore_errors else ""
    _columns = ["id", "data"]
    values: list[object] = [trace_id, json_string]
    if created_at is not None:
        _columns.append("created_at")
        values.append(created_at)
    columns = ", ".join(_columns)
    params = ",".join(["?" for _ in _columns])

    insert_sql = f"INSERT{ignore} INTO invocations({columns}) VALUES({params})"

    # We can't reuse a connection
    # because we're in a new thread
    with db_cursor(db_path, wal_mode) as cursor:
        cursor.execute(insert_sql, values)


def load_trace_from_db(db_path: Path, trace_id: str, wal_mode: bool = True) -> str:
    fetch_sql = "SELECT data FROM invocations WHERE id = ?"

    with db_cursor(db_path, wal_mode) as cursor:
        cursor.execute(fetch_sql, (trace_id,))
        row = cursor.fetchone()
    return row[0]


def list_traces_from_db(db_path: Path, wal_mode: bool = True):
    list_sql = """
    SELECT id, created_at, LENGTH(CAST(data AS BLOB)) FROM invocations
    ORDER BY id DESC LIMIT 500
    """

    with db_cursor(db_path, wal_mode) as cursor:
        cursor.execute(list_sql)
        rows = cursor.fetchall()
    return rows


def delete_traces_by_id(
    db_path: Path, trace_ids: Tuple[str, ...], wal_mode: bool = True
):
    params = ", ".join("?" * len(trace_ids))
    delete_sql = f"DELETE FROM invocations WHERE id in ({params})"

    with db_cursor(db_path, wal_mode) as cursor:
        cursor.execute(delete_sql, trace_ids)


def delete_traces_before(db_path: Path, before: datetime, wal_mode: bool = True):
    delete_sql = "DELETE FROM invocations WHERE (created_at < ?)"

    with db_cursor(db_path, wal_mode) as cursor:
        cursor.execute(delete_sql, (before,))
        cursor.execute("SELECT changes()")
        deleted_count = cursor.fetchone()[0]
    return deleted_count


def vacuum_db(db_path):
    with db_cursor(db_path, wal_mode=False) as cursor:
        cursor.execute("VACUUM")


def create_schema_table(cursor) -> None:
    create_table_query = """
    CREATE TABLE IF NOT EXISTS schemas (
        id integer PRIMARY KEY,
        created_at TEXT DEFAULT (STRFTIME('%Y-%m-%d %H:%M:%f', 'NOW')) NOT NULL,
        git_commit TEXT NULL,
        data text NOT NULL
    );
    """

    cursor.execute(create_table_query)


def save_schema(cursor, schema) -> None:
    from .git import COMMIT_SHA

    insert_sql = 'INSERT INTO schemas("data", "git_commit") VALUES(?, ?)'
    cursor.execute(insert_sql, (json.dumps(schema), COMMIT_SHA))


def load_schema(db_path: Path, wal_mode: bool = True) -> Tuple[Dict[str, Any], str]:
    load_sql = "SELECT data, git_commit FROM schemas ORDER BY created_at DESC LIMIT 1"

    with db_cursor(db_path) as cursor:
        cursor.execute(load_sql)
        data, commit = cursor.fetchone()

    data = json.loads(data)
    return data, commit
