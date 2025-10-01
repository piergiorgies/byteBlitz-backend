# ByteBlitz backend written in python with FastAPI

## how to start the app
Create the virtual environment with

`python -m venv .venv`

Activate the virtual environment

`source .venv/bin/activate`

Install the dependencies

`pip install -r requirements.txt`

Create your personal .env file starting from the example

`cp .env.example .env`

and modify the following fields (in .env file):

 - DATABASE_NAME
 - DATABASE_USER
 - DATABASE_PASSWORD

## Generate private key (P-384 curve)

`openssl ecparam -name secp384r1 -genkey -noout -out private.pem`

## Generate public key from private key

`openssl ec -in private.pem -pubout -out public.pem`

Copy the keys generated in the following field of the .env **escaping the newline with \n**

 - PRIVATE_KEY
 - PUBLIC_KEY

Follow the existing .env.example


## before start install postgres and pgadmin(optional) using docker

`docker compose up -d`

Verify that all services present in the docker compose are running

Go to pgAdmin and do the following step:

    -> login using the credential specified in the .env and docker-compose.yaml files 
    -> connect the database:
    -> right click on servers --> register --> Server...
    -> specifiy a server name (eg. local)
    -> in connection tab specify:
        - hostname(the docker internal ip of the container (like 172.x.x.x))
        - username(from .env file)
        - password(from .env file)
    -> after click save you should see local db in the left panel
    -> open the local server and create a new database by right clicking on databases field
    -> set the database name(from .env file)

At this point you should be able to create the database table running the following command

`python migrate.py migrate`

And create some data

`python migrate.py loaddata`

If the migation was successful you should see the table in the database, specifically under:

-> 'database_name' -> Schemas -> Tables

You can now start the application (without debug) with

`python main.py`

See if it works correctly by open http://127.0.0.1:9000/docs (this page is the integrated documentation od the api)

## Tests

If you want to test the application don't forget to run the following command in order to load the test dataset into your local instance of the database:

`python -m app.test.dataset`

**ATTENTION!** This operation will dump all your data from the database, so make sure not to run this unless you are completely sure about what you are about to do.