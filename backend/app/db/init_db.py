from sqlalchemy import inspect, text

from app.db.database import Base, engine
from app.models import db_models  # noqa: F401  (ensures models are registered)


def _ensure_deleted_at_column():
    # create_all() doesn't alter existing tables, so a pre-existing runs table needs
    # this column added by hand when upgrading from an older schema.
    inspector = inspect(engine)
    columns = [c["name"] for c in inspector.get_columns("runs")]
    if "deleted_at" not in columns:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE runs ADD COLUMN deleted_at DATETIME"))


def init_db():
    Base.metadata.create_all(bind=engine)
    _ensure_deleted_at_column()


if __name__ == "__main__":
    init_db()
