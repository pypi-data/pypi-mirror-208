from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional, cast

from chalk.clogging import chalk_logger
from chalk.features import FeatureConverter
from chalk.integrations.named import load_integration_variable
from chalk.sql._internal.sql_source import BaseSQLSource, validate_dtypes_for_efficient_execution
from chalk.sql.finalized_query import FinalizedChalkQuery
from chalk.utils.missing_dependency import missing_dependency_exception

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.url import URL


try:
    import sqlalchemy as sa
except ImportError:
    sa = None

if sa is None:
    _supported_sqlalchemy_types_for_pa_querying = ()
else:
    _supported_sqlalchemy_types_for_pa_querying = (
        sa.BigInteger,
        sa.Boolean,
        sa.BINARY,
        sa.BLOB,
        sa.LargeBinary,
        sa.Float,
        sa.Integer,
        sa.Time,
        sa.String,
        sa.Text,
        sa.VARBINARY,
        sa.DateTime,
        sa.Date,
        sa.SmallInteger,
        sa.BIGINT,
        sa.BOOLEAN,
        sa.CHAR,
        sa.DATETIME,
        sa.FLOAT,
        sa.INTEGER,
        sa.SMALLINT,
        sa.TEXT,
        sa.TIMESTAMP,
        sa.VARCHAR,
    )


class SnowflakeSourceImpl(BaseSQLSource):
    def __init__(
        self,
        *,
        name: Optional[str] = None,
        account_identifier: Optional[str] = None,
        warehouse: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        db: Optional[str] = None,
        schema: Optional[str] = None,
        role: Optional[str] = None,
        engine_args: Optional[Dict[str, Any]] = None,
    ):
        try:
            import snowflake.connector  # noqa
            import snowflake.sqlalchemy  # noqa
        except ModuleNotFoundError:
            raise missing_dependency_exception("chalkpy[snowflake]")
        del snowflake  # unused
        if engine_args is None:
            engine_args = {}
        engine_args.setdefault("pool_size", 20)
        engine_args.setdefault("max_overflow", 60)

        self.account_identifier = account_identifier or load_integration_variable(
            integration_name=name, name="SNOWFLAKE_ACCOUNT_ID"
        )
        self.warehouse = warehouse or load_integration_variable(integration_name=name, name="SNOWFLAKE_WAREHOUSE")
        self.user = user or load_integration_variable(integration_name=name, name="SNOWFLAKE_USER")
        self.password = password or load_integration_variable(integration_name=name, name="SNOWFLAKE_PASSWORD")
        self.db = db or load_integration_variable(integration_name=name, name="SNOWFLAKE_DATABASE")
        self.schema = schema or load_integration_variable(integration_name=name, name="SNOWFLAKE_SCHEMA")
        self.role = role or load_integration_variable(integration_name=name, name="SNOWFLAKE_ROLE")
        BaseSQLSource.__init__(self, name=name, engine_args=engine_args, async_engine_args={})

    def local_engine_url(self) -> URL:
        from sqlalchemy.engine.url import URL

        query = {
            k: v
            for k, v in (
                {
                    "database": self.db,
                    "schema": self.schema,
                    "warehouse": self.warehouse,
                    "role": self.role,
                }
            ).items()
            if v is not None
        }
        return URL.create(
            drivername="snowflake",
            username=self.user,
            password=self.password,
            host=self.account_identifier,
            query=query,
        )

    def execute_to_result_handles(
        self,
        finalized_query: FinalizedChalkQuery,
        columns_to_converters: Callable[[List[str]], Dict[str, FeatureConverter]],
        connection: Optional[Connection],
    ):
        # these imports are safe because the only way we end up here is if we have a valid SnowflakeSource constructed,
        # which already gates this import
        import snowflake.connector
        from sqlalchemy.sql import Select

        if isinstance(finalized_query.query, Select):
            validate_dtypes_for_efficient_execution(finalized_query.query, _supported_sqlalchemy_types_for_pa_querying)

        with (
            self.get_engine().connect() if connection is None else contextlib.nullcontext(connection)
        ) as sqlalchemy_cnx:
            con = cast(snowflake.connector.SnowflakeConnection, sqlalchemy_cnx.connection.dbapi_connection)
            chalk_logger.info("Established connection with Snowflake")
            sql, positional_params, named_params = self.compile_query(finalized_query)
            assert len(positional_params) == 0, "using named param style"
            with con.cursor() as cursor:
                chalk_logger.info("Acquired cursor for Snowflake query. Executing.")
                res = cursor.execute(sql, named_params)
                chalk_logger.info("Executed Snowflake query. Fetching results.")
                chalk_logger.info(f"Compiled query: {sql}")
                assert res is not None

                chalk_logger.info("Fetching result batches from snowflake.")
                ans = cursor.get_result_batches()
                assert ans is not None, "No batches returned"
                return ans

    def execute_to_batches(
        self,
        finalized_query: FinalizedChalkQuery,
        columns_to_converters: Callable[[List[str]], Dict[str, FeatureConverter]],
        connection: Optional[Connection],
    ):
        for b in self.execute_to_result_handles(finalized_query, columns_to_converters, connection):
            chalk_logger.info(f"Fetched batch with {b.uncompressed_size} bytes (uncompressed), {b.rowcount} rows.")
            yield b.to_arrow()

    def execute_query_efficient(
        self,
        finalized_query: FinalizedChalkQuery,
        columns_to_converters: Callable[[List[str]], Dict[str, FeatureConverter]],
        connection: Optional[Connection],
    ):
        # these imports are safe because the only way we end up here is if we have a valid SnowflakeSource constructed,
        # which already gates this import
        import snowflake.connector
        from sqlalchemy.sql import Select

        if isinstance(finalized_query.query, Select):
            validate_dtypes_for_efficient_execution(finalized_query.query, _supported_sqlalchemy_types_for_pa_querying)

        with (
            self.get_engine().connect() if connection is None else contextlib.nullcontext(connection)
        ) as sqlalchemy_cnx:
            con = cast(snowflake.connector.SnowflakeConnection, sqlalchemy_cnx.connection.dbapi_connection)
            chalk_logger.info("Established connection with Snowflake")
            sql, positional_params, named_params = self.compile_query(finalized_query)
            assert len(positional_params) == 0, "using named param style"
            with con.cursor() as cursor:
                chalk_logger.info("Acquired cursor for Snowflake query. Executing.")
                res = cursor.execute(sql, named_params)
                chalk_logger.info("Executed Snowflake query. Fetching results.")
                chalk_logger.info(f"Compiled query: {sql}")
                assert res is not None

                chalk_logger.info("Fetching arrow tables from Snowflake.")
                pa_table = cursor.fetch_arrow_all()

                if pa_table is None:
                    chalk_logger.info("Query returned no results.")
                    batches = cursor.get_result_batches()
                    assert batches is not None
                    return batches[0].to_arrow()

                chalk_logger.info(f"Received a PyArrow table from Snowflake with {len(pa_table)} rows.")
                return pa_table
