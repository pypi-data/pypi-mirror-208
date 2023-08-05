from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Optional

from chalk.integrations.named import load_integration_variable
from chalk.sql._internal.sql_source import BaseSQLSource
from chalk.utils.missing_dependency import missing_dependency_exception

if TYPE_CHECKING:
    from sqlalchemy.engine.url import URL


class RedshiftSourceImpl(BaseSQLSource):
    def __init__(
        self,
        host: Optional[str] = None,
        db: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        name: Optional[str] = None,
        engine_args: Optional[Dict[str, Any]] = None,
    ):
        try:
            import redshift_connector
        except ImportError:
            raise missing_dependency_exception("chalkpy[redshift]")
        del redshift_connector
        self.host = host or load_integration_variable(name="REDSHIFT_HOST", integration_name=name)
        self.db = db or load_integration_variable(name="REDSHIFT_DB", integration_name=name)
        self.user = user or load_integration_variable(name="REDSHIFT_USER", integration_name=name)
        self.password = password or load_integration_variable(name="REDSHIFT_PASSWORD", integration_name=name)
        if engine_args is None:
            engine_args = {}
        engine_args.setdefault("pool_size", 20)
        engine_args.setdefault("max_overflow", 60)
        engine_args.setdefault(
            "connect_args",
            {
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            },
        )
        # We set the default isolation level to autocommit since the SQL sources are read-only, and thus
        # transactions are not needed
        # Setting the isolation level on the engine, instead of the connection, avoids
        # a DBAPI statement to reset the transactional level back to the default before returning the
        # connection to the pool
        engine_args.setdefault("isolation_level", os.environ.get("CHALK_SQL_ISOLATION_LEVEL", "AUTOCOMMIT"))
        BaseSQLSource.__init__(self, name=name, engine_args=engine_args, async_engine_args={})

    def local_engine_url(self) -> URL:
        from sqlalchemy.engine.url import URL

        return URL.create(
            drivername="redshift+psycopg2",
            username=self.user,
            password=self.password,
            host=self.host,
            database=self.db,
        )
