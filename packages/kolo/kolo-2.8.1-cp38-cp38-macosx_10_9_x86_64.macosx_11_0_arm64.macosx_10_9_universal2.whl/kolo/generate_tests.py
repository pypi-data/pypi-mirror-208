from __future__ import annotations

import json
import platform
import re
from datetime import datetime
from functools import lru_cache, total_ordering
from typing import Dict, List
from urllib.parse import parse_qsl

import sqlglot
from jinja2 import Environment, PackageLoader

from .config import load_config
from .db import load_schema, load_trace_from_db, setup_db


class KoloPackageLoader(PackageLoader):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        # Work around UNC path mishandling:
        # https://github.com/pallets/jinja/issues/1675
        if platform.system() == "Windows":
            unc_prefix = "\\\\?\\"
            if self._template_root.startswith(unc_prefix):  # pragma: no cover
                self._template_root = self._template_root[len(unc_prefix) :]


def maybe_black(rendered):
    try:
        from black import format_file_contents
        from black.mode import Mode
        from black.parsing import InvalidInput
    except ImportError:  # pragma: no cover
        return rendered

    try:
        return format_file_contents(
            rendered, fast=True, mode=Mode(magic_trailing_comma=False)
        )
    except InvalidInput:  # pragma: no cover
        return rendered


env = Environment(loader=KoloPackageLoader("kolo"))


def _format_header(header: str) -> str:
    header = header.upper().replace("-", "_")
    if header in ("CONTENT_LENGTH", "CONTENT_TYPE"):
        return header
    return f"HTTP_{header}"


UUID_REPR_REGEX = re.compile(
    r"UUID\(\'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\'\)"
)


def parse_value(column, value, schema_data):
    column_schema = schema_data[column.table]["fields"][column.name]
    if column_schema["django_field"] == "django.db.models.fields.UUIDField":
        uuid_match = UUID_REPR_REGEX.match(str(value))
        if uuid_match:
            value = uuid_match[1]
    return value


@total_ordering
class DjangoField:
    def __init__(self, field, value):
        self.field = field
        self.value = repr(value) if isinstance(value, str) else value

    @classmethod
    def from_raw(cls, column, value, schema_data):
        field = schema_data[column.table]["fields"][column.name]["field_name"]
        return cls(field, value)

    def __eq__(self, other):
        return (self.field, self.value) == (other.field, other.value)

    def __lt__(self, other) -> bool:
        if self.field == other.field:
            return self.value < other.value
        return self.field < other.field

    def __hash__(self):
        return hash((self.field, self.value))

    def __repr__(self):
        return f'DjangoField("{self.field}", {self.value})'


class DjangoCreate:
    def __init__(self, table, model, values, import_path=None, query=None):
        self.table = table
        self.model = model
        self.values = values
        self.import_path = import_path
        self.query = query

    @classmethod
    def from_raw(cls, table, values, query, schema_data):
        module = schema_data[table]["model_module"]
        model = schema_data[table]["model_name"]
        return cls(table, f"{module}.{model}", tuple(values), f"import {module}", query)

    def __eq__(self, other):
        return (self.table, self.model, self.values) == (
            other.table,
            other.model,
            other.values,
        )

    def __hash__(self):
        return hash((self.table, self.model, self.values))

    def __repr__(self):
        return f'DjangoCreate("{self.table}", "{self.model}", {self.values})'


class DjangoQuery:
    def __init__(self, table, query):
        self.table = table
        self.query = query

    def __repr__(self):
        return f'DjangoQuery("{self.table}", {self.query})'

    def __eq__(self, other):
        return (self.table, self.query) == (other.table, other.query)


def make_table_sort_key(schema_data):
    tables = {}
    for table, data in schema_data.items():
        foreign_keys = []
        for field in data["fields"].values():
            if field["is_relation"] and not field["null"]:
                foreign_keys.append(field["related_model"])
        tables[table] = foreign_keys

    @lru_cache(maxsize=None)
    def table_depth(table):
        related_tables = tables[table]

        if len(related_tables) == 0:
            return 0
        return max(table_depth(related) for related in related_tables) + 1

    def sort_key(create):
        return (table_depth(create.table), create.table, create.values)

    return sort_key


def parse_columns(columns, row, schema_data):
    columns_by_table: Dict[str, List[DjangoField]] = {}
    for column, value in zip(columns, row):
        if not isinstance(column, sqlglot.exp.Column):
            continue

        field = DjangoField.from_raw(
            column,
            parse_value(column, value, schema_data),
            schema_data,
        )
        columns_by_table.setdefault(column.table, []).append(field)
    return columns_by_table


def parse_sql_queries(sql_queries, schema_data):
    # each select needs to become an insert
    inserts = set()
    imports = set()
    asserts = []
    seen_mutations = set()
    for query in sql_queries:
        if query["query_data"] is None:
            continue

        try:
            parsed_query = sqlglot.parse_one(query["query"], read="postgres")
        except sqlglot.errors.ParseError as e:  # pragma: no cover
            print("Error parsing query:")
            print(query["query"])
            print(e.errors)
            continue

        if isinstance(parsed_query, sqlglot.exp.Select):
            columns = [column for (_key, column) in parsed_query.iter_expressions()]
            for batch in query["query_data"]:
                for row in batch:
                    columns_by_table = parse_columns(columns, row, schema_data)

                    for table, row in columns_by_table.items():
                        if table in seen_mutations:
                            asserts.append(DjangoQuery(table, query))
                        else:
                            create = DjangoCreate.from_raw(
                                table, row, query, schema_data
                            )
                            inserts.add(create)
                            imports.add(create.import_path)
        else:
            _table = parsed_query.find(sqlglot.exp.Table)
            if _table is None:
                continue  # pragma: no cover
            query = DjangoQuery(_table.name, query)
            asserts.append(query)
            seen_mutations.add(_table.name)

    sql_fixtures: List[DjangoCreate | DjangoQuery] = sorted(
        inserts, key=make_table_sort_key(schema_data)
    )
    sql_fixtures.extend(asserts)
    return sql_fixtures, imports


def generate_from_trace_id(trace_id: str, test_class: str, test_name: str) -> str:
    config = load_config()
    wal_mode = config.get("wal_mode", True)
    db_path = setup_db(config)
    raw_data = load_trace_from_db(db_path, trace_id, wal_mode=wal_mode)
    data = json.loads(raw_data)
    frames = data["frames_of_interest"]

    served_request_frames = []
    current_served_request = None

    outbound_request_frames = []
    current_outbound_request = None

    sql_queries = []
    for frame in frames:
        if frame["type"] == "django_request":
            current_served_request = {"request": frame, "templates": []}
            served_request_frames.append(current_served_request)
        elif frame["type"] == "django_response":
            assert current_served_request is not None
            current_served_request["response"] = frame
            current_served_request = None
        elif frame["type"] == "django_template_start":
            assert current_served_request is not None
            current_served_request["templates"].append(frame["template"])
        elif frame["type"] == "outbound_http_request":
            if frame["subtype"] == "urllib3":
                # Only support requests from requests for now, to keep this simple
                continue
            assert current_outbound_request is None
            current_outbound_request = {"request": frame}
        elif frame["type"] == "outbound_http_response":
            if frame["subtype"] == "urllib3":
                continue
            assert current_outbound_request is not None
            current_outbound_request["response"] = frame
            outbound_request_frames.append(current_outbound_request)

            current_outbound_request = None
        elif frame["type"] == "end_sql_query":
            sql_queries.append(frame)

    if sql_queries:
        schema_data, git_commit = load_schema(db_path, wal_mode)
        sql_fixtures, imports = parse_sql_queries(sql_queries, schema_data)
    else:
        sql_fixtures = []
        imports = set()

    # Figure out further heuristics here..

    # We need to figure out some sort of data model for
    # - Which data gets mutated, which data only gets selected
    # We can't assume that we need to do inserts for a select
    # that happens on a table, after it gets mutated.
    # So let's keep a record of the order of queries, what tables they happen on
    # and if they select or only mutate.
    # Then we can actually tell which tables get mutated and in which ways.

    # This will be useful in the extension too to figure out
    # what were the rows that were created. What were the updates
    # that were actually made.

    # And then in the tests, we can make assertions around certain updates having happened

    request = served_request_frames[0]["request"]
    query_params = request["query_params"]
    query_params = f"{query_params}," if query_params else ""
    post_data = request["post_data"]
    post_data = f"{post_data}" if request["method"] == "POST" else ""

    request_headers = {
        _format_header(header): value for header, value in request["headers"].items()
    }
    if "HTTP_COOKIE" in request_headers and request_headers["HTTP_COOKIE"] == "":
        del request_headers["HTTP_COOKIE"]
    if "CONTENT_LENGTH" in request_headers:
        del request_headers["CONTENT_LENGTH"]
    if "HTTP_HOST" in request_headers:
        del request_headers["HTTP_HOST"]
    if "HTTP_X_FORWARDED_FOR" in request_headers:
        del request_headers["HTTP_X_FORWARDED_FOR"]
    if "HTTP_X_FORWARDED_PROTO" in request_headers:
        del request_headers["HTTP_X_FORWARDED_PROTO"]

    if "CONTENT_TYPE" in request_headers:
        # This is a special header, which ends up influencing
        # how the django test client formats different parts of the
        # request. It's provided to the test client as a lowercased
        # argument
        request_headers["content_type"] = request_headers["CONTENT_TYPE"]
        del request_headers["CONTENT_TYPE"]

    response = served_request_frames[0]["response"]
    template = env.get_template("django_request_test.py.j2")
    request_timestamp = datetime.utcfromtimestamp(request["timestamp"]).isoformat(
        timespec="seconds"
    )

    # So: How can we now format the body so that it becomes more readable
    # We can totally cater to just this urlencoded version first...

    # And it does kind of become immediately clear that custom
    # transformers are very much needed and desired.

    request_body = request["body"]

    content_type = request_headers.get("content_type", "")
    if content_type == "application/x-www-form-urlencoded":
        # TODO: Eventually need to be able to support multivaluedicts / query params with multiple values per key
        # I couldn't quite get that to work.
        # Custom request body formatting is clearly useful also here again..
        urldecoded_body = parse_qsl(request_body)
        prettified_request_body = f"urlencode({urldecoded_body})"
    elif "multipart/form-data" in content_type:
        prettified_request_body = post_data
        request_headers.pop("content_type")
    else:
        prettified_request_body = f'"{request_body}"'

    # Also look at httpretty alternatives...

    rendered = template.render(
        request=request,
        request_timestamp=request_timestamp,
        response=response,
        test_class=test_class,
        test_name=test_name,
        request_headers=request_headers,
        prettified_request_body=prettified_request_body,
        query_params=query_params,
        template_names=served_request_frames[0]["templates"],
        outbound_request_frames=outbound_request_frames,
        sql_fixtures=sql_fixtures,
        imports=sorted(imports),
    )
    return maybe_black(rendered)
