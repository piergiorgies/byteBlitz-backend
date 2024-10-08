from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session
from ..config import settings
#from ..models import Problem

#to run the dataset.py script, run the following command:
# python -m app.test.dataset

SQLALCHEMY_DATABASE_URL = settings.get_connection_string

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session : Session = Session(autocommit=False, autoflush=False, bind=engine)

#problem : Problem = session.query(Problem).filter(Problem.id == 1).first()

#print(problem)

print("Creating test dataset...")
#TODO: write a script to create a test dataset for the application
# 1. Clear all tables

metadata = MetaData()
metadata.reflect(bind=engine)

with session.begin():
    for table in reversed(metadata.sorted_tables):
        session.execute(table.delete())

print("All tables have been cleared.")
# 2. Create data
# 3. Cleate bonds between tables
# 4. Commit
# 5. Exceptions management
