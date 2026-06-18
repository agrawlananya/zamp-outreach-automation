from app.db.database import Base, engine
from app.models import db_models  # noqa: F401  (ensures models are registered)


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
