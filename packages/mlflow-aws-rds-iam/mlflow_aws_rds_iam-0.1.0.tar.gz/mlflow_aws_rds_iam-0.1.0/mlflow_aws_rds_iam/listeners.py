import logging
from typing import Callable

from mypy_boto3_rds.client import RDSClient
from sqlalchemy import Dialect
from sqlalchemy.pool import ConnectionPoolEntry

from .utils import DB_DEFAULT_PORT, DatabaseType

logger = logging.getLogger(__name__)


def make_token_provider(
    rds_client: RDSClient,
) -> Callable[[Dialect, ConnectionPoolEntry, dict[str, str], dict[str, str]], None]:
    def provide_token(
        dialect: Dialect,
        conn_rec: ConnectionPoolEntry,
        cargs: dict[str, str],
        cparams: dict[str, str],
    ) -> None:
        logger.debug("Renewing token for '%s'.", cparams["host"])

        # Inject AWS RDS IAM authentication token
        cparams["password"] = rds_client.generate_db_auth_token(
            DBHostname=cparams["host"],
            Port=int(cparams.get("port", DB_DEFAULT_PORT[DatabaseType(dialect.name)])),
            DBUsername=cparams["user"],
        )

    return provide_token
