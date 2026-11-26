"""Create the plate-scan tables inside the vehicle_recovery database."""

import sys

from app.database import create_schema, get_engine


def main() -> int:
    """Create any missing tables and print the names Postgres now has.

    Safe to run more than once. Existing tables are not dropped or altered.
    """
    try:
        engine = get_engine()
        create_schema(engine)
    except Exception as exc:
        # The driver message can include the connection URL. Print the type only.
        print(f"could not create tables: {exc.__class__.__name__}", file=sys.stderr)
        return 1

    from sqlalchemy import inspect

    names = sorted(inspect(engine).get_table_names())
    print("tables:", ", ".join(names))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
