import click
from app.config import settings
from app.database import engine
from sqlalchemy_utils import create_database, database_exists, drop_database

@click.group()
def cli():
    """ Management script for ByteBlitz """
    pass

# create a subcommand for the cli
@cli.command()
def migrate():
    """ Create the database if it doesn't exist and create all tables """
    db_name = settings.DATABASE_NAME

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

@cli.command
def load_data():
    """ Load the necessary data """
    click.echo("Loading data...")

    
if __name__ == '__main__':
    cli()