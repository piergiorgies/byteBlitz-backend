## do a migration with alembic

`alembic revision --autogenerate -m "Initial migration"`

## to push the migration to the DB:

`alembic upgrade head`