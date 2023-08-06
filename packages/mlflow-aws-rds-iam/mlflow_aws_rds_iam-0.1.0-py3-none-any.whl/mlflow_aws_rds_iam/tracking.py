import logging
import os
from urllib.parse import quote_plus

import boto3
from mlflow.store.tracking.sqlalchemy_store import SqlAlchemyStore
from sqlalchemy import event, make_url

from .listeners import make_token_provider
from .ssl import IS_SSL_DISABLED_ENV_VAR, set_ssl_params
from .utils import DatabaseType, get_db_default_port, get_db_type

logger = logging.getLogger(__name__)


class RDSIAMStore(SqlAlchemyStore):  # type: ignore[misc]
    def __init__(self, store_uri: str, artifact_uri: str):
        logger.debug("Using MLflow RDS IAM auth tracking store plugin.")

        db_uri = make_url(store_uri)

        if not get_db_type(db_uri) in DatabaseType:
            raise ValueError(
                "RDS IAM auth plugin for MLflow tracking only supports "
                "Postgresql and MySQL."
            )

        # Use SSL database connection with CA verification unless explicitly disabled
        if not os.getenv(IS_SSL_DISABLED_ENV_VAR, "False").lower() in ("true", "1"):
            db_uri = set_ssl_params(db_uri)
        else:
            logger.warning("SSL tracking store database connection is disabled.")

        # Do not use RDS IAM tokens if a password is defined
        if db_uri.password:
            logger.debug("Using tracking store database password auth.")
            super().__init__(
                db_uri.render_as_string(hide_password=False),
                default_artifact_root=artifact_uri,
            )
            return

        logger.debug("Using tracking store RDS IAM token auth.")
        if not db_uri.host or not db_uri.username:
            raise ValueError(
                "RDS IAM authentication requires a URI with a host and user."
            )

        rds = boto3.client("rds")

        # Bootstrap URL with initial RDS IAM token
        db_uri = db_uri.set(
            password=quote_plus(
                rds.generate_db_auth_token(
                    DBHostname=db_uri.host,
                    Port=db_uri.port or get_db_default_port(db_uri),
                    DBUsername=db_uri.username,
                )
            )
        )
        logger.debug(
            "Tracking store bootstrap database URI: %s", db_uri.render_as_string()
        )

        # Let MLflow's own SqlAlchemyStore initialize the SA engine
        super().__init__(
            db_uri.render_as_string(hide_password=False),
            default_artifact_root=artifact_uri,
        )

        # Add token rotation listener to the engine
        event.listen(self.engine, "do_connect", make_token_provider(rds))
