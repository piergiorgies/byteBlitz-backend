# ByteBlitz backend written in python with FastAPI


`docker compose up -d`

Verify that all services present in the docker compose are running


## how to start the app
Create the virtual environment with

`python -m venv .venv`

Activate the virtual environment

`source .venv/bin/activate`

Install the dependencies

`pip install -r requirements.txt`

Create your personal .env file starting from the example

`cp .env.example .env`

and modify the following fields:

 - DATABASE_NAME
 - DATABASE_USER
 - DATABASE_PASSWORD

## before start install postgres and pgadmin(optional)


Start the application (without debug) with

`python app/main.py`
