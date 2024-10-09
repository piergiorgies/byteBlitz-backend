from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..config import settings

#to run the dataset.py script, run the following command:
# python -m app.test.dataset

# db connection
SQLALCHEMY_DATABASE_URL = settings.get_connection_string
engine = create_engine(SQLALCHEMY_DATABASE_URL)
session : Session = Session(autocommit=False, autoflush=False, bind=engine)
metadata : MetaData = MetaData()
metadata.reflect(bind=engine)

print("Creating test dataset...")

try:
    
    # Clear all tables
    with session.begin():
        for table in reversed(metadata.sorted_tables):
            print(table)
            #TODO: exclude alembic_version table
            #session.execute(table.delete())

    print("All tables have been cleared")

    # Create data
    #TODO: from here on
    # contests
    # languages
    # submission_results
    # teams
    # user_types
    # contest_teams
    # users
    # contest_users
    # problems
    # team_users
    # contest_problems
    # problem_constraints
    # problem_test_cases
    # submissions
    # contest_submissions
    # submission_test_cases

    #TODO: here
    # Create bonds between tables
    # Commit

except SQLAlchemyError as e:
    session.rollback()
    print("Database error: " + str(e))
    raise e
except Exception as e:
    session.rollback()
    print("An unexpected error occurred: " + str(e))
    raise e