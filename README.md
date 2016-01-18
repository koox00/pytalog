# Pytalog

A Python-Flask application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.

With JSON endpoints and atom feeds for restaurants

# Install

If you have vagrant installed just cd in the project directory and run vagrant up.

If you don't have vagrant you have to manually install all the requirements listed in the requirements.txt

e.g: `pip install --user Flask-SQLAlchemy`

Once installed you can run the following commands:

create the db and all the tables

    python manage.py initdb

seed the db with dummy data

    python manage.py seeddb

drop the database

    python manage.py dropdb

start a server.

    python manage.py runserver

Once the server is run you can access the application in `0.0.0.0:5000`.

## Google oauth API

For the google login you have to add your credentials. First rename the example file.

    mv client_secrets.example.json client_secrets.json

Then add your api username and secret


# TODO

- implement a file logger
- use blueprints to break down the application into:
  - api (json and atom endpoints)
  - auth (login, logout, and providers)
  - main
- create tests
- create a seperate file for config
