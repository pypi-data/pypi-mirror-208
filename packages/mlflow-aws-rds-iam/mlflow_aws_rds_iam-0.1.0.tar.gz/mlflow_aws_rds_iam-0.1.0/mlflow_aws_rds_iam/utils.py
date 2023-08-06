from sqlalchemy.engine import URL

try:
    from enum import StrEnum
except ImportError:
    from strenum import StrEnum  # type: ignore[import,no-redef]


class DatabaseType(StrEnum):
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"


DB_DEFAULT_PORT: dict[DatabaseType, int] = {
    DatabaseType.POSTGRESQL: 5432,
    DatabaseType.MYSQL: 3306,
}


def get_db_type(uri: URL) -> DatabaseType:
    return DatabaseType(uri.drivername.split("+")[0])


def get_db_default_port(uri: URL) -> int:
    return DB_DEFAULT_PORT[get_db_type(uri)]
