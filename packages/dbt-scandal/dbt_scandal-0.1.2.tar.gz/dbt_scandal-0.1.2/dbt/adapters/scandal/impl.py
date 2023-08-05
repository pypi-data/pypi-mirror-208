from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

import agate  # type:ignore
import pandas as pd
import pyarrow as pa  # type:ignore

from dbt.adapters.base.impl import BaseAdapter
from dbt.adapters.base.meta import available
from dbt.adapters.base.relation import BaseRelation
from dbt.adapters.factory import FACTORY
from dbt.adapters.reference_keys import _make_ref_key_msg
from dbt.adapters.scandal.connections import DummyCredentials, ScandalConnectionManager
from dbt.contracts.connection import Connection
from dbt.contracts.relation import RelationType
from dbt.events.functions import fire_event
from dbt.events.types import SchemaCreation, SchemaDrop
from dbt.exceptions import RelationTypeNullError

NORMALIZED_SOURCE_NAMES = {"BigQuery": "bigquery", "Redshift": "redshift", "PostgreSQL": "postgres"}
LIST_RELATIONS_MACRO_NAME = "list_relations_without_caching"
GET_COLUMNS_IN_RELATION_MACRO_NAME = "get_columns_in_relation"
LIST_SCHEMAS_MACRO_NAME = "list_schemas"
CHECK_SCHEMA_EXISTS_MACRO_NAME = "check_schema_exists"
CREATE_SCHEMA_MACRO_NAME = "create_schema"
DROP_SCHEMA_MACRO_NAME = "drop_schema"
RENAME_RELATION_MACRO_NAME = "rename_relation"
TRUNCATE_RELATION_MACRO_NAME = "truncate_relation"
DROP_RELATION_MACRO_NAME = "drop_relation"
ALTER_COLUMN_TYPE_MACRO_NAME = "alter_column_type"


@contextmanager
def _release_plugin_lock():
    FACTORY.lock.release()
    try:
        yield
    finally:
        FACTORY.lock.acquire()


class ScandalAdapter(BaseAdapter):
    RELATION_TYPES = {
        "TABLE": RelationType.Table,
        "VIEW": RelationType.View,
        "EXTERNAL": RelationType.External,
    }

    ConnectionManager = ScandalConnectionManager
    delegate: BaseAdapter

    def __init__(self, config) -> None:
        super().__init__(config)

        self.connections.set_connection_name()
        source_type = adbc_parse_source(adbc_get_info(self.connections.get_thread_connection()))
        delegate_adapter_name = NORMALIZED_SOURCE_NAMES[source_type]

        with _release_plugin_lock():
            FACTORY.load_plugin(delegate_adapter_name)
            our_plugin = FACTORY.get_plugin_by_name(config.credentials.type)
            our_plugin.dependencies = [delegate_adapter_name]

            # Hack, register_adapter looks at the credentials type to determine which one to load, temporarily override
            original_creds = config.credentials
            config.credentials = DummyCredentials(db_type=delegate_adapter_name)
            FACTORY.register_adapter(config)
            config.credentials = original_creds

            self.Relation = FACTORY.get_relation_class_by_name(delegate_adapter_name)  # type:ignore

        # HACK: Forward all of _available_ and _parse_replacements_ to underlying adapter

        # This adapter was created in register_adapter earlier, protocol is different to base class
        self.delegate: BaseAdapter = FACTORY.lookup_adapter(delegate_adapter_name)  # type:ignore

        # self._available_ is set by metaclass=AdapterMeta
        self._available_ = self.delegate._available_.union(self._available_)  # type:ignore
        # self._parse_replacements_ is set by metaclass=AdapterMeta
        self._parse_replacements_.update(self.delegate._parse_replacements_)  # type:ignore
        ScandalAdapter.delegate = self.delegate

    @classmethod
    def date_function(cls):
        """
        Returns canonical date func
        """
        return "datenow()"

    @available.parse(lambda *a, **k: (None, None))
    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        """Add a query to the current transaction. A thin wrapper around
        ConnectionManager.add_query.

        :param sql: The SQL query to add
        :param auto_begin: If set and there is no transaction in progress,
            begin a new one.
        :param bindings: An optional list of bindings for the query.
        :param abridge_sql_log: If set, limit the raw sql logged to 512
            characters
        """
        return self.connections.add_query(sql, auto_begin, bindings, abridge_sql_log)  # type:ignore

    @classmethod
    def convert_text_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_text_type(agate_table, col_idx)

    @classmethod
    def convert_number_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_number_type(agate_table, col_idx)

    @classmethod
    def convert_boolean_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_boolean_type(agate_table, col_idx)

    @classmethod
    def convert_datetime_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_datetime_type(agate_table, col_idx)

    @classmethod
    def convert_date_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_date_type(agate_table, col_idx)

    @classmethod
    def convert_time_type(cls, agate_table: agate.Table, col_idx: int) -> str:
        return cls.delegate.convert_time_type(agate_table, col_idx)

    @classmethod
    def is_cancelable(cls) -> bool:
        return cls.delegate.is_cancelable()

    def expand_column_types(self, goal, current):
        return self.delegate.expand_column_types(goal, current)

    def alter_column_type(self, relation, column_name, new_column_type) -> None:
        """
        1. Create a new column (w/ temp name and correct type)
        2. Copy data over to it
        3. Drop the existing column (cascade!)
        4. Rename the new column to existing column
        """
        kwargs = {
            "relation": relation,
            "column_name": column_name,
            "new_column_type": new_column_type,
        }
        self.execute_macro(ALTER_COLUMN_TYPE_MACRO_NAME, kwargs=kwargs)

    def drop_relation(self, relation):
        if relation.type is None:
            raise RelationTypeNullError(relation)

        self.cache_dropped(relation)
        self.execute_macro(DROP_RELATION_MACRO_NAME, kwargs={"relation": relation})

    def truncate_relation(self, relation):
        self.execute_macro(TRUNCATE_RELATION_MACRO_NAME, kwargs={"relation": relation})

    def rename_relation(self, from_relation, to_relation):
        self.cache_renamed(from_relation, to_relation)

        kwargs = {"from_relation": from_relation, "to_relation": to_relation}
        self.execute_macro(RENAME_RELATION_MACRO_NAME, kwargs=kwargs)

    def get_columns_in_relation(self, relation):
        return self.execute_macro(GET_COLUMNS_IN_RELATION_MACRO_NAME, kwargs={"relation": relation})

    def create_schema(self, relation: BaseRelation) -> None:
        relation = relation.without_identifier()
        fire_event(SchemaCreation(relation=_make_ref_key_msg(relation)))
        kwargs = {
            "relation": relation,
        }
        self.execute_macro(CREATE_SCHEMA_MACRO_NAME, kwargs=kwargs)
        self.commit_if_has_connection()
        # we can't update the cache here, as if the schema already existed we
        # don't want to (incorrectly) say that it's empty

    def drop_schema(self, relation: BaseRelation) -> None:
        relation = relation.without_identifier()
        fire_event(SchemaDrop(relation=_make_ref_key_msg(relation)))
        kwargs = {
            "relation": relation,
        }
        self.execute_macro(DROP_SCHEMA_MACRO_NAME, kwargs=kwargs)
        self.commit_if_has_connection()
        # we can update the cache here
        self.cache.drop_schema(relation.database, relation.schema)

    def list_relations_without_caching(
        self,
        schema_relation: BaseRelation,
    ) -> List[BaseRelation]:
        # NOTE: adbc doesn't filter listing of tables, we do our own until we fix it
        res = (
            self.connections.get_thread_connection()
            .handle.adbc_get_objects(
                depth="tables", catalog_filter=schema_relation.database, db_schema_filter=schema_relation.schema
            )
            .read_all()
            .to_pylist()
        )
        tables = [
            schema["db_schema_tables"]
            for schema in res[0]["catalog_db_schemas"]
            if schema["db_schema_name"] == schema_relation.schema
        ][0]

        relations = []
        quote_policy = {"database": True, "schema": True, "identifier": True}
        for table in tables:
            relations.append(
                self.Relation.create(
                    database=schema_relation.database,
                    schema=schema_relation.schema,
                    identifier=table["table_name"],
                    quote_policy=quote_policy,
                    type=self.RELATION_TYPES.get(table["table_type"], RelationType.External),
                )
            )
        return relations

    def quote(self, identifier):
        return self.delegate.quote(identifier)

    def list_schemas(self, database: str) -> List[str]:
        ret = (
            self.connections.get_thread_connection().handle.adbc_get_objects(depth="db_schemas").read_all().to_pylist()
        )

        return [table["db_schema_name"] for table in ret[0]["catalog_db_schemas"]]

    def check_schema_exists(self, database: str, schema: str) -> bool:
        return (
            self.connections.get_thread_connection().handle.adbc_get_objects(depth="db_schemas").read_all().to_pylist()
        )

    @available.parse_none
    def ingest_table(self, database, schema, table_name, agate_table, column_override):
        conn = self.connections.get_thread_connection()
        # TODO(robert): column overrides need to be valid pandas dtypes - is that good/fine?
        df = pd.read_csv(agate_table.original_abspath, engine="pyarrow", dtype_backend="pyarrow", dtype=column_override)
        pa_table = pa.Table.from_pandas(df)
        with conn.handle.cursor() as curr:
            curr.adbc_ingest(f"${database}.${schema}.${table_name}", pa_table)

    @available
    def quote_column_value(self, value, datatype):
        return f"'{value}'" if not isinstance(datatype, agate.Number) else value

    # This is for use in the test suite
    def run_sql_for_tests(self, sql, fetch, conn):
        cursor = conn.handle.cursor()
        try:
            cursor.execute(sql)
            if hasattr(conn.handle, "commit"):
                conn.handle.commit()
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "all":
                return cursor.fetchall()
            else:
                return
        except BaseException as e:
            if conn.handle and not getattr(conn.handle, "closed", True):
                conn.handle.rollback()
            print(sql)
            print(e)
            raise
        finally:
            conn.transaction_open = False

    def __getattr__(self, item):
        """
        Directly proxy to the DB adapter, Python adapter in this case does what we explicitly define in this class.
        """
        if hasattr(self.delegate, item):
            return getattr(self.delegate, item)
        else:
            getattr(super(), item)


def adbc_get_info(conn) -> List[Dict[str, Any]]:
    """
    Get FlightSql info of the driver.
    """
    handle = conn.handle.adbc_connection.get_info()
    reader = pa.RecordBatchReader._import_from_c(handle.address)
    return reader.read_all().to_pylist()


def adbc_parse_source(infos: List[Dict[str, Any]]):
    source_name = [entry["info_value"] for entry in infos if entry["info_name"] == 0][0]
    # This assumes format "scandal [<sourceName>]". Has to match what the server is sending us
    return source_name[9:-1]
