import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from app.database import Base
from app.models import *
from app.config import settings

@pytest.fixture(scope='module')
def engine():
    # Use an in-memory SQLite database for testing
    return create_engine(settings.get_test_connection_string)

@pytest.fixture(scope='module')
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope='function')
def session(engine, tables):
    """Create a new database session for a test."""
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    # Rollback any changes made during the test
    session.rollback()
    session.close()

def test_create_user(session):
    user_type = UserType(code='admin', description='Administrator', permissions=1)
    user = User(username='test_user', password='password', email='test@example.com', user_type=user_type)
    
    session.add(user_type)
    session.add(user)
    session.commit()

    assert user.id is not None
    assert user.username == 'test_user'
    assert user.user_type == user_type

def test_create_problem(session):
    user_type = UserType(code='author', description='Problem Author', permissions=2)
    user = User(username='author_user', password='password', email='author@example.com', user_type=user_type)
    session.add(user_type)
    session.add(user)
    session.commit()

    problem = Problem(title='Sample Problem', description='A simple problem.', points=100, author=user)
    session.add(problem)
    session.commit()

    assert problem.id is not None
    assert problem.title == 'Sample Problem'
    assert problem.author == user

def test_create_submission(session):
    user_type = UserType(code='solver', description='Problem Solver', permissions=3)
    user = User(username='solver_user', password='password', email='solver@example.com', user_type=user_type)
    problem = Problem(title='Sample Problem', description='A simple problem.', points=100, author=user)
    language = Language(name='python', file_extension='py')
    submission_result = SubmissionResult(code='AC', description='Accepted')
    session.add(user_type)
    session.add(user)
    session.add(problem)
    session.add(language)
    session.add(submission_result)
    session.commit()

    submission = Submission(notes='First submission', problem=problem, user=user, language_id=1, submission_result_id=1)
    session.add(submission)
    session.commit()

    assert submission.id is not None
    assert submission.problem == problem
    assert submission.user == user

def test_create_contest(session):
    contest = Contest(name='Sample Contest', start_datetime=datetime.now(), end_datetime=datetime.now())
    session.add(contest)
    session.commit()

    assert contest.id is not None
    assert contest.name == 'Sample Contest'

def test_add_user_to_contest(session):
    user_type = UserType(code='participant', description='Contest Participant', permissions=4)
    user = User(username='contestant', password='password', email='contestant@example.com', user_type=user_type)
    contest = Contest(name='Another Contest', start_datetime=datetime.now(), end_datetime=datetime.now())
    session.add(user_type)
    session.add(user)
    session.add(contest)
    session.commit()

    contest_user = ContestUser(user_id=user.id, contest_id=contest.id)
    session.add(contest_user)
    session.commit()

    assert contest_user.user_id == user.id
    assert contest_user.contest_id == contest.id

    # Ensure the relationship works
    assert user in contest.users
    assert contest in user.contests
