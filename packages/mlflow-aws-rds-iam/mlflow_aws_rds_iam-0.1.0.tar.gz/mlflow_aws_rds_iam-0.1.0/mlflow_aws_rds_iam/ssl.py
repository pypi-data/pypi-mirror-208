from importlib.resources import as_file, files

from sqlalchemy.engine import URL

from .utils import DatabaseType, get_db_type

IS_SSL_DISABLED_ENV_VAR = "MLFLOW_DISABLE_DB_SSL"
CERT_PATH = "certs/global-bundle.pem"


def set_ssl_params(uri: URL) -> URL:
    with as_file(files(__package__).joinpath(CERT_PATH)) as certfile:
        match get_db_type(uri):
            case DatabaseType.POSTGRESQL:
                ssl_params = {"sslmode": "verify-ca", "sslrootcert": str(certfile)}
            case DatabaseType.MYSQL:
                ssl_params = {"ssl-mode": "VERIFY_CA", "ssl-ca": str(certfile)}
            case _:
                raise ValueError(
                    "Only SSL parameters for Postresql or MySQL URIs are supported."
                )

    return uri.set(query=uri.query | ssl_params)
