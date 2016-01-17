# Pytalog

A Python-Flask application that provides a list of items within a variety of categories as well as provide a user registration and authentication system. Registered users have the ability to post, edit and delete their own items.

With JSON endpoints and atom feeds for restaurants

# Install

If you have vagrant installed just cd in the project directory and run vagrant up.

If you don't have vagrant you have to manually install all the requirements listed in the requirements.txt

Once installed you can run the following commands:

    python manage.py initdb

creates the db and all the tables

    python manage.py seeddb

seeds the db with dummy data

    python manage.py dropdb

drops the database

    python manage.py runserver

runs a server. Once run you can access the application in `0.0.0.0:5000`


# TODO

- implement a file logger
- use blueprints to break down the application into:
  - api (json and atom endpoints)
  - auth (login, logout, and providers)
  - main
- create tests
