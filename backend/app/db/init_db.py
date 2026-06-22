from sqlalchemy import inspect, text

from app.db.database import Base, engine
from app.models import db_models  # noqa: F401  (ensures models are registered)


# Columns added to `runs` after the table's original shape. create_all() never alters an
# existing table, so when upgrading from an older schema each must be added by hand or the
# ORM's SELECT (which lists every mapped column) fails with "no such column".
_RUNS_ADDED_COLUMNS = {
    "deleted_at": "DATETIME",
    "fixture_id": "VARCHAR",
}


def _ensure_runs_columns():
    inspector = inspect(engine)
    if not inspector.has_table("runs"):
        return
    existing = {c["name"] for c in inspector.get_columns("runs")}
    for column, ddl_type in _RUNS_ADDED_COLUMNS.items():
        if column not in existing:
            with engine.begin() as conn:
                conn.execute(text(f"ALTER TABLE runs ADD COLUMN {column} {ddl_type}"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_runs_columns()


if __name__ == "__main__":
    init_db()
