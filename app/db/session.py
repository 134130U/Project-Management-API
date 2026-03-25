from sqlalchemy.orm import Session
from app.db.database import SessionLocal


class DBSession:

    def __enter__(self):

        self.db = SessionLocal()

        return self.db


    def __exit__(

        self,
        exc_type,
        exc,
        tb
    ):
        self.db.close()