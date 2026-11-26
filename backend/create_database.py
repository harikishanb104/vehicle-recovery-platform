"""Create the empty vehicle_recovery database if it does not already exist."""

import re
import sys

from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url

from app.config import DATABASE_URL

DB_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def main() -> int:
    """Create the application database and leave its tables for create_schema().

    Connecting to the postgres maintenance database is required because
    CREATE DATABASE cannot run inside the database being created.
    """
    if not DATABASE_URL:
        print("DATABASE_URL is not set. Copy backend/.env.example to backend/.env.", file=sys.stderr)
        return 1

    url = make_url(DATABASE_URL)
    db_name = url.database
    if not db_name or not DB_NAME_PATTERN.match(db_name):
        print("DATABASE_URL must use a simple database name such as vehicle_recovery.", file=sys.stderr)
        return 1

    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin_engine.connect() as connection:
        exists = connection.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": db_name},
        ).scalar()
        if exists:
            print(f"database {db_name} already exists")
            return 0
        connection.execute(text(f'CREATE DATABASE "{db_name}"'))
        print(f"created database {db_name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
