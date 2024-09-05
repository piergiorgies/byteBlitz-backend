from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .config import settings

SQLALCHEMY_DATABASE_URL = settings.get_connection_string

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class QueryBuilder():
    model = None
    query = None
    limit: int = None
    offset: int = None

    def __init__(self, model, session: Session, limit=15, offset=None):
        self.model = model
        self.query = session.query(model)
        self.limit = limit
        self.offset = offset
        self._build()

    def _build(self):
        if self.limit:
            self.query = self.query.limit(self.limit)
        if self.offset:
            self.query = self.query.offset(self.offset)
    
    def get(self):
        return self.query.all()
    
    def count(self):
        return self.query.count()
