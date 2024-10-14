from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from .config import settings
from typing import Any

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
    """
    A class to build list queries

    """

    model = None
    query = None
    limit: int = None
    offset: int = None
    record_count: int = None

    def __init__(self, model, session: Session, limit, offset):
        self.model = model
        self.query = session.query(model)
        self.limit = limit
        self.offset = offset
        self._build()

    def _build(self):
        self.record_count = self.query.count()
        if self.limit:
            self.query = self.query.limit(self.limit)
        if self.offset:
            self.query = self.query.offset(self.offset)

    def getQuery(self):
        return self.query
    
    def getCount(self):
        return self.record_count
    
def get_object_by_id(model, session: Session, id: int) -> Any:
    """
    Get an object by its ID

    Args:
        model (Base): The model class (has to be a subclass of Base)
        session (Session): The session
        id (int): The ID of the object

    Returns:
        Base: The object
    """
    return session.query(model).filter(model.id == id).first()

def get_object_by_id_joined_with(model, session: Session, id: int, join_fields: list[str]) -> Any:
    """
    Get an object by its ID

    Args:
        model (Base): The model class (has to be a subclass of Base)
        session (Session): The session
        id (int): The ID of the object
        join_fields (list[str]): The fields to join with

    Returns:
        Base: The object
    """
    query = session.query(model)
    for field in join_fields:
        query = query.join(field)
    return query.filter(model.id == id).first()
