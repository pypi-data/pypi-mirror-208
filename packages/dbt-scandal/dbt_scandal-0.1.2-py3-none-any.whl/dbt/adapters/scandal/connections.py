import copy
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import agate  # type:ignore
from scandal import connect  # type:ignore

import dbt.clients.agate_helper
import dbt.exceptions  # noqa
from dbt.adapters.sql.connections import SQLConnectionManager
from dbt.contracts.connection import AdapterRequiredConfig, AdapterResponse, Connection, Credentials
from dbt.events.adapter_endpoint import AdapterLogger
from dbt.events.contextvars import get_node_info
from dbt.events.functions import fire_event
from dbt.events.types import ConnectionUsed, SQLQuery, SQLQueryStatus
from dbt.utils import cast_to_str

logger = AdapterLogger("Scandal")

DEFAULT_HOSTS = {"localhost": "http://localhost:7444", "cloud": "https://crowbar.fly.dev:7774"}


@dataclass
class ScandalCredentials(Credentials):
    """
    Defines database specific credentials that get added to
    profiles.yml to connect to new adapter
    """

    organization: str
    project: str
    host: str = "cloud"

    @property
    def type(self):
        """Return name of adapter."""
        return ScandalConnectionManager.TYPE

    @property
    def unique_field(self):
        """
        Hashed and included in anonymous telemetry to track adapter adoption.
        Pick a field that can uniquely identify one team/organization building with this adapter
        """
        return self.database

    def _connection_keys(self):
        """
        List of keys to display in the `dbt debug` output.
        """
        return "host", "database", "schema", "organization", "source"

    @classmethod
    def validate(cls, data: Any):
        pass

    @classmethod
    def __pre_deserialize__(cls, d: Dict[Any, Any]) -> Dict[Any, Any]:
        d2 = dict(copy.deepcopy(d))
        if "host" in d2 in list(DEFAULT_HOSTS.keys()):
            d2["host"] = DEFAULT_HOSTS[d2["host"]]

        with connect(org=d2["organization"], project=d2["project"]) as conn:
            d2["database"] = conn.adbc_get_objects(depth="catalogs").read_all().to_pylist()[0]["catalog_name"]
        return d2


@dataclass
class DummyCredentials(Credentials):
    db_type: str = ""
    database: str = ""
    schema: str = ""

    def _connection_keys(self):
        return ()

    @property
    def type(self):
        return self.db_type

    @property
    def unique_field(self):
        return self.db_type


class ScandalConnectionManager(SQLConnectionManager):
    TYPE: str = "scandal"

    def __init__(self, profile: AdapterRequiredConfig):
        super().__init__(profile)

    @contextmanager
    # The result of applying contextmanager gives us a function that returns context manager.
    # Underlying function has to return generator or iterator
    def exception_handler(self, sql: str):
        """Create a context manager that handles exceptions caused by database
        interactions.

        :param str sql: The SQL string that the block inside the context
            manager is executing.
        :return: A context manager that handles exceptions raised by the
            underlying database.
        """
        try:
            yield
        except dbt.exceptions.DbtRuntimeError:
            raise
        except RuntimeError as e:
            logger.info("Scandal error: {}", str(e))
            raise e
        except Exception as exc:
            logger.info("Error running SQL: {}", sql)
            logger.info("Rolling back transaction.")
            raise dbt.exceptions.DbtRuntimeError(str(exc)) from exc

    def cancel(self, connection: Connection):
        """Cancel the given connection."""
        pass

    @classmethod
    def open(cls, connection: Connection) -> Connection:
        """Open the given connection on the adapter and return it.

        This may mutate the given connection (in particular, its state and its
        handle).

        This should be thread-safe, or hold the lock if necessary. The given
        connection should not be in either in_use or available.
        """

        def exponential_backoff(attempt: int):
            return attempt * attempt

        return cls.retry_connection(
            connection=connection,
            connect=lambda: connect(
                org=connection.credentials.organization, project=connection.credentials.project  # type:ignore
            ),
            logger=logger,
            retry_limit=5,
            retry_timeout=exponential_backoff,
            retryable_exceptions=[],
        )

    def add_begin_query(self, *args, **kwargs):
        pass

    def add_commit_query(self, *args, **kwargs):
        pass

    def begin(self):
        pass

    def commit(self):
        pass

    def clear_transaction(self):
        pass

    def execute(self, sql: str, auto_begin: bool = False, fetch: bool = False) -> Tuple[AdapterResponse, agate.Table]:
        """Execute the given SQL.

        :param str sql: The sql to execute.
        :param bool auto_begin: If set, and dbt is not currently inside a
            transaction, automatically begin one.
        :param bool fetch: If set, fetch results.
        :return: A tuple of the query status and results (empty if fetch=False).
        :rtype: Tuple[AdapterResponse, agate.Table]
        """
        sql = self._add_query_comment(sql)
        _, cursor = self.add_query(sql, auto_begin)
        try:
            response = self.get_response(cursor)
            if fetch:
                table = self.get_result_from_cursor(cursor)
            else:
                cursor.fetchone()
                table = dbt.clients.agate_helper.empty_table()
            return response, table
        finally:
            cursor.close()

    def add_query(
        self,
        sql: str,
        auto_begin: bool = True,
        bindings: Optional[Any] = None,
        abridge_sql_log: bool = False,
    ) -> Tuple[Connection, Any]:
        connection = self.get_thread_connection()
        if auto_begin and connection.transaction_open is False:
            self.begin()
        fire_event(
            ConnectionUsed(
                conn_type=self.TYPE,
                conn_name=cast_to_str(connection.name),
                node_info=get_node_info(),
            )
        )

        with self.exception_handler(sql):
            if abridge_sql_log:
                log_sql = "{}...".format(sql[:512])
            else:
                log_sql = sql

            fire_event(SQLQuery(conn_name=cast_to_str(connection.name), sql=log_sql, node_info=get_node_info()))
            pre = time.time()

            # Close cursor if execute fails, otherwise ADBC gets upset about unclosed children
            cursor = connection.handle.cursor()
            try:
                cursor.execute(sql, bindings)
            except Exception as exc:
                cursor.close()
                raise exc

            fire_event(
                SQLQueryStatus(
                    status=str(self.get_response(cursor)),
                    elapsed=round((time.time() - pre)),
                    node_info=get_node_info(),
                )
            )

            return connection, cursor

    @classmethod
    def get_response(cls, cursor) -> AdapterResponse:
        return AdapterResponse(_message="OK", rows_affected=cursor.rowcount)
