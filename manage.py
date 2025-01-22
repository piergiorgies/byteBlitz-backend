import click
from sqlalchemy_utils import create_database, database_exists, drop_database
from sqlalchemy.orm import Session
from typing import List

from app.config import settings
from app.database import engine
from app.models import User, UserType, Language, SubmissionResult
from app.database import get_session
from app.auth_util.pwd_util import _hash_password

@click.group()
def cli():
    """ Management script for ByteBlitz """
    pass

@cli.command()
def migrate():
    """ Create the database if it doesn't exist and create all tables """
    db_name = settings.DATABASE_NAME
    try:
        if not database_exists(engine.url):
            create_database(engine.url)
            click.echo(f"Database {db_name} created successfully")
        else:
            click.echo(f"Database {db_name} already exists")
    
        click.echo("Creating tables...")
        
        # run the alembic migrations
        from alembic.config import Config
        from alembic import command
    
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
    
        click.echo("Tables created successfully")

    except Exception as e:
        click.echo(f"Error: {e}")

@cli.command()
def loaddata():
    """ Load the necessary data """
    click.echo("Loading data...")
    # Create a session
    session_generator = get_session()
    session: Session = next(session_generator)

    # Create the user types
    try:
        user_types: List[UserType] = [
            UserType(
                id=1,
                code="Guest",
                description="Unregistered user",
                permissions=0
            ),
            UserType(
                id=2,
                code="User",
                description="Registered user",
                permissions=1
            ),
            UserType(
                id=3,
                code="Problem Maintainer",
                description="Maintains problems",
                permissions=1 << 1
            ),
            UserType(
                id=4,
                code="Contest Maintainer",
                description="Maintains contests",
                permissions=1 << 2
            ),
            UserType(
                id=5,
                code="User Maintainer",
                description="Maintains users",
                permissions=1 << 3
            ),
            UserType(
                id=6,
                code="Admin",
                description="Site administrator",
                permissions=(1 << 7) - 1
            ),
            UserType(
                id=7,
                code="Judge",
                description="Judges problems",
                permissions=1 << 7
            )
        ]
        # Add the user types to the session
        session.add_all(user_types)
        session.commit()

    except Exception as e:
        click.echo(f"Error: {e}")
        pass

    # Create the users
    try:
        password = 'ApoChair2023!'
        password_hash, salt = _hash_password(password)
        users : List[User] = [
            User(
                username="guest",
                email="guest@guest.com",
                password_hash="guest",
                salt="guest",
                user_type_id=1
            ),
            User(
                username="admin",
                email="admin@admin.com",
                password_hash=password_hash,
                salt=salt,
                user_type_id=6
            ),
            User(
                username="user",
                email="user@user.com",
                password_hash=password_hash,
                salt=salt,
                user_type_id=2
            )
        ]
        session.add_all(users)
        session.commit()
    
    except Exception as e:
        click.echo(f"Error: {e}")

    # Create languages
    try:
        languages: List[Language] = [
            Language(
                id=1,
                name="C",
                file_extension="c"
            ),
            Language(
                id=2,
                name="C++",
                file_extension="cpp"
            ),
            Language(
                id=3,
                name="Python",
                file_extension="py"
            ),
            Language(
                id=4,
                name="Java",
                file_extension="java"
            ),
            Language(
                id=5,
                name="Rust",
                file_extension="rs"
            )
        ]
        session.add_all(languages)
        session.commit()

    except Exception as e:
        click.echo(f"Error: {e}")
    
    # Create the submission results

    try:
        results : List[SubmissionResult] = [
            SubmissionResult(
                id=1,
                code="AC",
                description="Accepted"
            ),
            SubmissionResult(
                id=2,
                code="WA",
                description="Wrong Answer"
            ),
            SubmissionResult(
                id=3,
                code="TLE",
                description="Time Limit Exceeded"
            ),
            SubmissionResult(
                id=4,
                code="MLE",
                description="Memory Limit Exceeded"
            ),
            SubmissionResult(
                id=5,
                code="CE",
                description="Compilation Error"
            )
        ]

        session.add_all(results)
        session.commit()

    except Exception as e:
        click.echo(f"Error: {e}")



    click.echo("Data loaded successfully")


if __name__ == "__main__":
    cli()